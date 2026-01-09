import sys
import os
import time
# Add the AIVideo folder to path so 'sora_tool' package is found
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sora_tool.core.persistence import PersistenceManager
from sora_tool.core.account_manager import AccountManager
from sora_tool.core.mock_sora_client import MockSoraClient
from sora_tool.core.queue_engine import QueueEngine
from sora_tool.core.state_machine import JobStateMachine
from sora_tool.core.scheduler import Scheduler
from sora_tool.core.models import JobStatus

def test_full_flow():
    print(">>> Starting Test Simulation...")
    db_path = "test_sora.db"
    if os.path.exists(db_path):
        os.remove(db_path)

    persistence = PersistenceManager(db_path)
    account_manager = AccountManager(persistence)
    sora_client = MockSoraClient()
    queue = QueueEngine(persistence)
    sm = JobStateMachine(persistence, account_manager, sora_client)
    scheduler = Scheduler(queue, sm, interval=0.3)

    account_manager.add_account("cookie_abc", "acc_1")
    print("   [Created Account acc_1]")

    job = queue.add_job("A beautiful sunset over Tokyo")
    print(f"   [Created Job {job.id[:8]}...]")

    scheduler.start()
    print("   [Waiting for completion...]")
    
    for i in range(30):
        updated_job = queue.get_job(job.id)
        print(f"   Tick {i}: Status = {updated_job.status}")
        if updated_job.status == JobStatus.DONE.value:
            print(">>> SUCCESS: Job finished!")
            break
        if updated_job.status == JobStatus.FAILED.value:
            print(">>> FAILURE: Job failed!")
            break
        time.sleep(0.3)
    else:
        print(">>> TIMEOUT")
    
    scheduler.stop()
    print(">>> Test Complete.")

if __name__ == "__main__":
    test_full_flow()
