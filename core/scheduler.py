import time
import threading
from typing import Optional
from .queue_engine import QueueEngine
from .state_machine import JobStateMachine

class Scheduler:
    def __init__(self, queue: QueueEngine, state_machine: JobStateMachine, interval=1.0):
        self.queue = queue
        self.state_machine = state_machine
        self.interval = interval
        self.is_running = False
        self.thread: Optional[threading.Thread] = None

    def start(self):
        if self.is_running:
            return
        self.is_running = True
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=2)

    def _run_loop(self):
        while self.is_running:
            try:
                self.tick()
            except Exception as e:
                print(f"Scheduler error: {e}")
            time.sleep(self.interval)

    def tick(self):
        for job in self.queue.get_active_jobs():
            self.state_machine.process_tick(job)
