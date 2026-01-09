"""
Sora API Adapter - Real API implementation.
Replaces MockSoraClient without modifying Core Engine.

IMPORTANT:
- NO SECRETS IN CODE
- Respects kill-switch and feature flags
- Shadow mode = read-only (no create_video)
"""
import time
import uuid
import requests
from typing import Optional, Dict, List
from .sora_client_interface import SoraClientInterface
from .config import config
from .auth_store import auth_store
from .telemetry import telemetry

class SoraApiAdapter(SoraClientInterface):
    """
    Real Sora API adapter that implements SoraClientInterface.
    Drop-in replacement for MockSoraClient.
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
        })
        # Endpoints loaded from config or environment
        self._base_url = config.get("api_base_url", "")

    def _check_kill_switch(self):
        """Raise exception if kill switch is active."""
        if config.get("kill_switch", False):
            raise Exception("KILL_SWITCH: All API calls disabled")

    def _get_headers(self, account_id: str) -> Dict[str, str]:
        """Build headers with auth cookies."""
        headers = {}
        cookie = auth_store.get_cookie_header(account_id)
        if cookie:
            headers["Cookie"] = cookie
        token = auth_store.get_access_token(account_id)
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers

    def create_video(self, account_cookie: str, prompt: str, **kwargs) -> str:
        """
        Create video via Sora API.
        In shadow mode, returns a fake ID without calling API.
        """
        self._check_kill_switch()
        
        # Shadow mode = read-only, don't actually create
        if config.is_shadow_mode:
            print("[SHADOW MODE] create_video skipped - returning mock ID")
            return f"shadow_{uuid.uuid4().hex[:8]}"

        request_id = uuid.uuid4().hex
        telemetry.start_request(request_id)
        
        try:
            # Rate limiting
            time.sleep(config.get("rate_limit_delay", 2.0))
            
            # TODO: Replace with actual Sora endpoint when reversed
            # This is a placeholder structure
            response = self.session.post(
                f"{self._base_url}/v1/videos/generate",
                headers=self._get_headers(account_cookie),
                json={"prompt": prompt, **kwargs},
                timeout=config.get("request_timeout", 30)
            )
            
            if response.status_code == 401:
                telemetry.end_request(request_id, "create_video", False, "401")
                raise Exception("401 Unauthorized")
            elif response.status_code == 429:
                telemetry.end_request(request_id, "create_video", False, "429")
                raise Exception("429 Too Many Requests")
            
            response.raise_for_status()
            data = response.json()
            video_id = data.get("id", data.get("video_id", ""))
            
            telemetry.end_request(request_id, "create_video", True)
            return video_id
            
        except requests.RequestException as e:
            telemetry.end_request(request_id, "create_video", False, "network")
            raise Exception(f"Network error: {e}")

    def get_status(self, video_id: str) -> str:
        """Get video generation status."""
        self._check_kill_switch()
        
        # Shadow mode still works for status checks
        if video_id.startswith("shadow_"):
            return "finished"  # Pretend it finished

        request_id = uuid.uuid4().hex
        telemetry.start_request(request_id)
        
        try:
            response = self.session.get(
                f"{self._base_url}/v1/videos/{video_id}/status",
                timeout=config.get("request_timeout", 30)
            )
            response.raise_for_status()
            data = response.json()
            
            status = data.get("status", "processing")
            telemetry.end_request(request_id, "get_status", True)
            return status
            
        except requests.RequestException as e:
            telemetry.end_request(request_id, "get_status", False, "network")
            raise Exception(f"Network error: {e}")

    def download_video(self, video_id: str, path: str) -> None:
        """Download finished video."""
        self._check_kill_switch()
        
        # Shadow mode
        if video_id.startswith("shadow_"):
            with open(path, 'w') as f:
                f.write(f"Shadow mode mock content for {video_id}")
            return

        request_id = uuid.uuid4().hex
        telemetry.start_request(request_id)
        
        try:
            response = self.session.get(
                f"{self._base_url}/v1/videos/{video_id}/download",
                stream=True,
                timeout=config.get("request_timeout", 60)
            )
            response.raise_for_status()
            
            with open(path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            telemetry.end_request(request_id, "download_video", True)
            
        except requests.RequestException as e:
            telemetry.end_request(request_id, "download_video", False, "network")
            raise Exception(f"Download error: {e}")

    def get_history(self, account_cookie: str, limit: int = 5) -> list:
        """Get recent video history for idempotency checks."""
        self._check_kill_switch()
        
        request_id = uuid.uuid4().hex
        telemetry.start_request(request_id)
        
        try:
            response = self.session.get(
                f"{self._base_url}/v1/videos/history",
                headers=self._get_headers(account_cookie),
                params={"limit": limit},
                timeout=config.get("request_timeout", 30)
            )
            response.raise_for_status()
            data = response.json()
            
            telemetry.end_request(request_id, "get_history", True)
            return data.get("videos", [])
            
        except requests.RequestException as e:
            telemetry.end_request(request_id, "get_history", False, "network")
            return []  # Return empty on error, don't crash

    def is_healthy(self) -> bool:
        """Check if API is reachable."""
        if config.get("kill_switch", False):
            return False
        if not self._base_url:
            return False
        try:
            response = self.session.get(
                f"{self._base_url}/health",
                timeout=5
            )
            return response.status_code == 200
        except:
            return False
