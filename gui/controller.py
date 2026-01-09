"""
Controller Layer - GLUE between GUI and Core Engine.
NO business logic here. Only routing and state observation.
"""
import threading
import time
import sys
import os
from typing import Callable, List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

# Ensure path is set for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Core imports (absolute)
from sora_tool.core.persistence import PersistenceManager
from sora_tool.core.account_manager import AccountManager
from sora_tool.core.client_factory import create_sora_client
from sora_tool.core.queue_engine import QueueEngine
from sora_tool.core.state_machine import JobStateMachine
from sora_tool.core.scheduler import Scheduler
from sora_tool.core.config import config
from sora_tool.core.models import Job, Account, JobStatus
from sora_tool.core.telemetry import telemetry

class EngineState(Enum):
    STOPPED = "stopped"
    RUNNING = "running"
    PAUSED = "paused"

@dataclass
class ControllerEvent:
    """Event emitted by Controller to GUI."""
    event_type: str  # "jobs_updated", "accounts_updated", "log", "state_changed"
    data: Any = None

class AppController:
    """
    Orchestrator between GUI and Core Engine.
    - Initializes Core components
    - Provides read-only views of state for GUI
    - Routes GUI commands to Core
    - Emits events for GUI to observe
    """
    
    def __init__(self, db_path: str = "sora_manager.db"):
        # Core Components
        self.persistence = PersistenceManager(db_path)
        self.account_manager = AccountManager(self.persistence)
        self.sora_client = create_sora_client()
        self.queue = QueueEngine(self.persistence)
        self.state_machine = JobStateMachine(
            self.persistence, self.account_manager, self.sora_client
        )
        self.scheduler = Scheduler(self.queue, self.state_machine, interval=1.0)
        
        # Controller State
        self.engine_state = EngineState.STOPPED
        self._event_listeners: List[Callable[[ControllerEvent], None]] = []
        self._log_buffer: List[str] = []
        self._polling_thread: Optional[threading.Thread] = None
        self._polling = False

    # ===== Event System =====
    def add_listener(self, callback: Callable[[ControllerEvent], None]):
        """Subscribe to controller events."""
        self._event_listeners.append(callback)

    def _emit(self, event_type: str, data: Any = None):
        """Emit event to all listeners."""
        event = ControllerEvent(event_type, data)
        for listener in self._event_listeners:
            try:
                listener(event)
            except Exception as e:
                self._log(f"Event listener error: {e}")

    def _log(self, message: str):
        """Add log message and emit to GUI."""
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self._log_buffer.append(log_entry)
        # Keep buffer size reasonable
        if len(self._log_buffer) > 500:
            self._log_buffer = self._log_buffer[-250:]
        self._emit("log", log_entry)

    # ===== Commands (GUI -> Core) =====
    def start(self):
        """Start the scheduler."""
        if self.engine_state == EngineState.RUNNING:
            return
        self.scheduler.start()
        self.engine_state = EngineState.RUNNING
        self._start_polling()
        self._log("Engine STARTED")
        self._emit("state_changed", self.engine_state)

    def pause(self):
        """Pause the scheduler."""
        if self.engine_state != EngineState.RUNNING:
            return
        self.scheduler.stop()
        self.engine_state = EngineState.PAUSED
        self._log("Engine PAUSED")
        self._emit("state_changed", self.engine_state)

    def resume(self):
        """Resume the scheduler."""
        if self.engine_state != EngineState.PAUSED:
            return
        self.start()

    def stop(self):
        """Stop the scheduler completely."""
        self.scheduler.stop()
        self._stop_polling()
        self.engine_state = EngineState.STOPPED
        self._log("Engine STOPPED")
        self._emit("state_changed", self.engine_state)

    def activate_kill_switch(self):
        """Emergency stop + disable real API."""
        config.activate_kill_switch()
        self.stop()
        self._log("⚠️ KILL SWITCH ACTIVATED")
        self._emit("state_changed", self.engine_state)

    def add_job(self, prompt: str) -> Job:
        """Add a new job to the queue."""
        job = self.queue.add_job(prompt)
        self._log(f"Job added: {job.id[:8]}...")
        self._emit("jobs_updated", None)
        return job

    def add_account(self, account_id: str, cookie: str = ""):
        """Add a new account."""
        self.account_manager.add_account(cookie, account_id)
        self._log(f"Account added: {account_id}")
        self._emit("accounts_updated", None)

    # ===== Config Toggles =====
    def set_use_real_api(self, enabled: bool):
        """Toggle real API usage."""
        if enabled:
            config.enable_real_api(shadow_mode=config.is_shadow_mode)
        else:
            config.disable_real_api()
        # Recreate client with new config
        self.sora_client = create_sora_client()
        self.state_machine.sora_client = self.sora_client
        self._log(f"Real API: {'ENABLED' if enabled else 'DISABLED'}")

    def set_shadow_mode(self, enabled: bool):
        """Toggle shadow mode."""
        config.set("shadow_mode", enabled)
        self._log(f"Shadow Mode: {'ON' if enabled else 'OFF'}")

    # ===== Queries (GUI reads state) =====
    def get_jobs(self) -> List[Dict]:
        """Get all jobs as dicts for GUI display."""
        jobs = self.queue.get_all_jobs()
        return [{
            "id": j.id[:8] + "...",
            "full_id": j.id,
            "status": j.status,
            "prompt": j.prompt_text[:30] + "..." if len(j.prompt_text) > 30 else j.prompt_text,
            "retry_count": j.retry_count,
            "account": j.account_id[:10] if j.account_id else "-",
            "next_retry": time.strftime("%H:%M:%S", time.localtime(j.next_retry_at)) if j.next_retry_at > 0 else "-"
        } for j in jobs]

    def get_accounts(self) -> List[Dict]:
        """Get all accounts as dicts for GUI display."""
        return [{
            "id": a.id,
            "status": a.status,
            "quota": f"{a.quota_used_today}/{a.quota_daily_limit}",
            "cooldown": time.strftime("%H:%M:%S", time.localtime(a.cooldown_until)) if a.cooldown_until > time.time() else "-"
        } for a in self.account_manager.accounts]

    def get_logs(self) -> List[str]:
        """Get log buffer."""
        return self._log_buffer.copy()

    def get_config_state(self) -> Dict:
        """Get current config for GUI toggles."""
        return {
            "use_real_api": config.use_real_api,
            "shadow_mode": config.is_shadow_mode,
            "kill_switch": config.get("kill_switch", False),
            "engine_state": self.engine_state.value
        }

    def get_telemetry(self) -> Dict:
        """Get telemetry stats."""
        return telemetry.get_stats()

    # ===== Polling for GUI updates =====
    def _start_polling(self):
        """Start background thread to emit periodic updates."""
        if self._polling:
            return
        self._polling = True
        self._polling_thread = threading.Thread(target=self._poll_loop, daemon=True)
        self._polling_thread.start()

    def _stop_polling(self):
        """Stop polling thread."""
        self._polling = False

    def _poll_loop(self):
        """Emit updates every second for GUI refresh."""
        while self._polling:
            self._emit("jobs_updated", None)
            self._emit("accounts_updated", None)
            time.sleep(1)
