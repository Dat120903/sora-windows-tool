"""
Read-Only API Integration Test
Phase 4B-1: Tests get_history, get_status, download_video with real cookies.

PREREQUISITES:
1. Export cookies from sora.com using Cookie-Editor extension
2. Save as JSON to: ~/.sora_tool/auth/cookies_export.json
3. Run this script

USAGE:
    python tests/test_readonly_api.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pathlib import Path
from sora_tool.core.config import config
from sora_tool.core.auth_store import auth_store
from sora_tool.core.sora_api_adapter import SoraApiAdapter
from sora_tool.core.telemetry import telemetry

# Account ID for testing
TEST_ACCOUNT = "test_sora_account"

# Expected cookie file location (repo/auth/cookies_export.json)
PROJECT_ROOT = Path(__file__).parent.parent
COOKIE_FILE = PROJECT_ROOT / "auth" / "cookies_export.json"


def step_import_cookies():
    """Step 1: Import cookies from file."""
    print("\n" + "=" * 50)
    print("STEP 1: Import Cookies")
    print("=" * 50)
    
    if not COOKIE_FILE.exists():
        print(f"\n[ERROR] Cookie file not found: {COOKIE_FILE}")
        print("\nPlease:")
        print("1. Login to sora.com in your browser")
        print("2. Install 'Cookie-Editor' extension")
        print("3. Export cookies as JSON")
        print(f"4. Save to: {COOKIE_FILE}")
        return False
    
    success = auth_store.import_from_file(TEST_ACCOUNT, str(COOKIE_FILE))
    if not success:
        print("\n[ERROR] Failed to import cookies")
        return False
    
    print("\n✅ Cookies imported successfully")
    return True


def step_test_get_history():
    """Step 2: Test get_history endpoint."""
    print("\n" + "=" * 50)
    print("STEP 2: Test get_history")
    print("=" * 50)
    
    config.enable_real_api(shadow_mode=False)
    adapter = SoraApiAdapter()
    
    try:
        print("\n[INFO] Calling get_history...")
        videos = adapter.get_history(TEST_ACCOUNT, limit=5)
        
        if not videos:
            print("\n[WARNING] No videos returned (may be empty account or auth issue)")
            return None
        
        print(f"\n✅ Retrieved {len(videos)} videos:")
        for i, video in enumerate(videos[:3]):
            video_id = video.get("id", video.get("video_id", "unknown"))
            status = video.get("status", video.get("state", "unknown"))
            print(f"  {i+1}. ID: {video_id[:20]}... | Status: {status}")
        
        # Return first video for next tests
        return videos[0] if videos else None
        
    except Exception as e:
        print(f"\n❌ get_history failed: {e}")
        return None


def step_test_get_status(video):
    """Step 3: Test get_status endpoint."""
    print("\n" + "=" * 50)
    print("STEP 3: Test get_status")
    print("=" * 50)
    
    if not video:
        print("\n[SKIP] No video available from history")
        return False
    
    video_id = video.get("id", video.get("video_id"))
    if not video_id:
        print("\n[SKIP] Could not extract video ID")
        return False
    
    adapter = SoraApiAdapter()
    
    try:
        print(f"\n[INFO] Checking status for: {video_id[:30]}...")
        status = adapter.get_status(video_id, TEST_ACCOUNT)
        print(f"\n✅ Status: {status}")
        return status == "completed"
        
    except Exception as e:
        print(f"\n❌ get_status failed: {e}")
        return False


def step_test_download(video):
    """Step 4: Test download_video endpoint."""
    print("\n" + "=" * 50)
    print("STEP 4: Test download_video")
    print("=" * 50)
    
    if not video:
        print("\n[SKIP] No video available")
        return False
    
    video_id = video.get("id", video.get("video_id"))
    status = video.get("status", video.get("state", ""))
    
    if status not in ["completed", "done", "finished", "ready"]:
        print(f"\n[SKIP] Video not completed (status: {status})")
        return False
    
    adapter = SoraApiAdapter()
    download_path = Path("downloads") / f"test_{video_id[:8]}.mp4"
    
    try:
        print(f"\n[INFO] Downloading to: {download_path}")
        adapter.download_video(video_id, str(download_path), TEST_ACCOUNT)
        
        if download_path.exists():
            size = download_path.stat().st_size
            print(f"\n✅ Downloaded: {size:,} bytes")
            return True
        else:
            print("\n❌ Download file not created")
            return False
            
    except Exception as e:
        print(f"\n❌ download_video failed: {e}")
        return False


def show_telemetry():
    """Show telemetry summary."""
    print("\n" + "=" * 50)
    print("TELEMETRY SUMMARY")
    print("=" * 50)
    stats = telemetry.get_stats()
    print(f"\nTotal requests: {stats.get('total_requests', 0)}")
    print(f"Success rate: {stats.get('success_rate', 0):.1%}")
    print(f"Avg latency: {stats.get('avg_latency_ms', 0):.0f}ms")
    if stats.get('error_breakdown'):
        print(f"Errors: {stats['error_breakdown']}")


def main():
    print("\n" + "#" * 50)
    print("# Phase 4B-1: Read-Only API Integration Test")
    print("#" * 50)
    
    # Step 1: Import cookies
    if not step_import_cookies():
        print("\n❌ TEST FAILED: Could not import cookies")
        sys.exit(1)
    
    # Step 2: Test get_history
    video = step_test_get_history()
    
    # Step 3: Test get_status
    status_ok = step_test_get_status(video)
    
    # Step 4: Test download
    download_ok = step_test_download(video)
    
    # Show stats
    show_telemetry()
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    print(f"  Cookies Import: ✅")
    print(f"  get_history:    {'✅' if video else '⚠️ Empty'}")
    print(f"  get_status:     {'✅' if status_ok else '⚠️'}")
    print(f"  download_video: {'✅' if download_ok else '⚠️'}")
    
    # Cleanup
    config.disable_real_api()
    print("\n[Cleanup] Reverted to mock mode")
    print("\n" + "#" * 50)


if __name__ == "__main__":
    main()
