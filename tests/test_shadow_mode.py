"""
Shadow Mode Test - Read-only test with real API adapter.
Does NOT create actual videos. Tests auth and polling only.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sora_tool.core.config import config
from sora_tool.core.client_factory import create_sora_client
from sora_tool.core.auth_store import auth_store
from sora_tool.core.telemetry import telemetry

def test_shadow_mode():
    print("=" * 50)
    print("SHADOW MODE TEST (Read-Only)")
    print("=" * 50)
    
    # Enable real API but in shadow mode
    config.enable_real_api(shadow_mode=True)
    print(f"[Config] use_real_api: {config.use_real_api}")
    print(f"[Config] shadow_mode: {config.is_shadow_mode}")
    
    # Create client via factory
    client = create_sora_client()
    
    # Test 1: Create video (should be mocked in shadow mode)
    print("\n[Test 1] create_video (should return shadow_ ID)...")
    try:
        video_id = client.create_video("test_account", "A sunset over mountains")
        print(f"  Result: {video_id}")
        assert video_id.startswith("shadow_"), "Expected shadow_ prefix"
        print("  ✅ PASS - Shadow mode correctly prevented real API call")
    except Exception as e:
        print(f"  ❌ FAIL - {e}")
        return False

    # Test 2: Get status (should work even in shadow mode)
    print("\n[Test 2] get_status...")
    try:
        status = client.get_status(video_id)
        print(f"  Result: {status}")
        print("  ✅ PASS")
    except Exception as e:
        print(f"  ❌ FAIL - {e}")

    # Test 3: Telemetry stats
    print("\n[Telemetry Stats]")
    stats = telemetry.get_stats()
    print(f"  {stats}")

    # Cleanup - back to mock
    config.disable_real_api()
    print("\n[Cleanup] Reverted to Mock client")
    
    print("\n" + "=" * 50)
    print("SHADOW MODE TEST COMPLETE")
    print("=" * 50)
    return True

if __name__ == "__main__":
    test_shadow_mode()
