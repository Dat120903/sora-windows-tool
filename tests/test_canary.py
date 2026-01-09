"""
Canary Test - Single job test with full flow.
Use this AFTER shadow mode test passes.
"""
import sys
import os
import time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sora_tool.core.config import config
from sora_tool.core.persistence import PersistenceManager
from sora_tool.core.account_manager import AccountManager
from sora_tool.core.client_factory import create_sora_client
from sora_tool.core.queue_engine import QueueEngine
from sora_tool.core.state_machine import JobStateMachine
from sora_tool.core.scheduler import Scheduler
from sora_tool.core.models import JobStatus
from sora_tool.core.telemetry import telemetry

def test_canary(use_real_api: bool = False):
    print("=" * 50)
    print(f"CANARY TEST (1 Job) - Real API: {use_real_api}")
    print("=" * 50)
    
    # Setup
    db_path = "canary_test.db"
    if os.path.exists(db_path):
        os.remove(db_path)
    
    if use_real_api:
        config.enable_real_api(shadow_mode=False)  # Full real mode
    else:
        config.disable_real_api()  # Mock mode
    
    # Init components
    persistence = PersistenceManager(db_path)
    account_manager = AccountManager(persistence)
    sora_client = create_sora_client()
    queue = QueueEngine(persistence)
    sm = JobStateMachine(persistence, account_manager, sora_client)
    scheduler = Scheduler(queue, sm, interval=0.5)
    
    # Add test account
    account_manager.add_account("canary_cookie", "canary_acc")
    print("[Setup] Created canary account")
    
    # Add single job
    job = queue.add_job("Canary test - a simple animation")
    print(f"[Setup] Created job {job.id[:8]}...")
    
    # Run
    scheduler.start()
    print("[Running] Scheduler started...")
    
    success = False
    for i in range(30):
        updated = queue.get_job(job.id)
        print(f"  Tick {i}: {updated.status}")
        
        if updated.status == JobStatus.DONE.value:
            print("\n✅ CANARY PASSED - Job completed successfully!")
            success = True
            break
        elif updated.status == JobStatus.FAILED.value:
            print(f"\n❌ CANARY FAILED - Job failed")
            print(f"   Errors: {updated.error_log}")
            break
        
        time.sleep(0.5)
    else:
        print("\n⚠️ CANARY TIMEOUT")
    
    scheduler.stop()
    
    # Stats
    print("\n[Telemetry]")
    print(f"  {telemetry.get_stats()}")
    
    # Cleanup
    config.disable_real_api()
    if os.path.exists(db_path):
        os.remove(db_path)
    
    print("=" * 50)
    return success

if __name__ == "__main__":
    # Run with mock first
    print("\n>>> Running canary with MOCK client...\n")
    test_canary(use_real_api=False)
    
    # Uncomment below to test with real API (careful!)
    # print("\n>>> Running canary with REAL API...\n")
    # test_canary(use_real_api=True)
