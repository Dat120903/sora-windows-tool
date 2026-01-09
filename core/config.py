"""
Configuration and Feature Flags for Sora Tool.
All flags default to SAFE/OFF state.
"""
import os
import json
from typing import Dict, Any
from pathlib import Path

# Config file location (outside repo, in user data)
CONFIG_DIR = Path.home() / ".sora_tool"
CONFIG_FILE = CONFIG_DIR / "config.json"

DEFAULT_CONFIG = {
    # Feature Flags
    "use_real_api": False,          # DEFAULT OFF - use mock
    "shadow_mode": True,            # Read-only mode when real API enabled
    "kill_switch": False,           # Emergency stop all API calls
    
    # API Settings (NO SECRETS - these are just identifiers)
    "api_base_url": "",             # Set at runtime, not hardcoded
    
    # Telemetry
    "enable_telemetry": True,       # Track latency, error counts
    
    # Safety
    "max_retries": 5,
    "request_timeout": 30,
    "rate_limit_delay": 2.0,        # Seconds between requests
}

class Config:
    _instance = None
    _config: Dict[str, Any] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load()
        return cls._instance

    def _load(self):
        """Load config from file, merge with defaults."""
        self._config = DEFAULT_CONFIG.copy()
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, 'r') as f:
                    user_config = json.load(f)
                    self._config.update(user_config)
            except Exception:
                pass  # Use defaults on error

    def save(self):
        """Persist config to file."""
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_FILE, 'w') as f:
            json.dump(self._config, f, indent=2)

    def get(self, key: str, default=None):
        return self._config.get(key, default)

    def set(self, key: str, value: Any):
        self._config[key] = value
        self.save()

    @property
    def use_real_api(self) -> bool:
        """Check if real API is enabled AND kill switch is OFF."""
        if self._config.get("kill_switch", False):
            return False  # Kill switch overrides everything
        return self._config.get("use_real_api", False)

    @property
    def is_shadow_mode(self) -> bool:
        """Shadow mode = real API but read-only (no create_video)."""
        return self._config.get("shadow_mode", True)

    def activate_kill_switch(self):
        """Emergency stop - immediately disable all real API calls."""
        self._config["kill_switch"] = True
        self._config["use_real_api"] = False
        self.save()
        print("[KILL SWITCH ACTIVATED] All real API calls disabled.")

    def enable_real_api(self, shadow_mode: bool = True):
        """Enable real API. Shadow mode ON by default for safety."""
        self._config["use_real_api"] = True
        self._config["shadow_mode"] = shadow_mode
        self._config["kill_switch"] = False
        self.save()

    def disable_real_api(self):
        """Revert to mock client."""
        self._config["use_real_api"] = False
        self.save()

# Singleton instance
config = Config()
