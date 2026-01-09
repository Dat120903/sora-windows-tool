"""
Sora API Adapter - Real API implementation.
Replaces MockSoraClient without modifying Core Engine.

IMPORTANT:
- NO SECRETS IN CODE
- Respects kill-switch and feature flags
- Shadow mode = read-only (no create_video)
- Phase 4B-1: Read-only endpoints only (get_history, get_status, download_video)
- create_video remains shadow-only until Phase 4B-2
"""
import time
import uuid
import os
import requests
from typing import Optional, Dict, List
from .sora_client_interface import SoraClientInterface
from .config import config
from .auth_store import auth_store
from .telemetry import telemetry

# Sora API base URL (correct domain)
SORA_BASE_URL = "https://sora.chatgpt.com"

class SoraApiAdapter(SoraClientInterface):
    """
    Real Sora API adapter that implements SoraClientInterface.
    Drop-in replacement for MockSoraClient.
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Origin": SORA_BASE_URL,
            "Referer": f"{SORA_BASE_URL}/",
        })
        self._base_url = config.get("api_base_url") or SORA_BASE_URL

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
        return headers

    def _handle_response_errors(self, response, request_id: str, endpoint: str):
        """Handle common HTTP errors."""
        if response.status_code == 401:
            telemetry.end_request(request_id, endpoint, False, "401")
            raise Exception("401 Unauthorized - Session expired or invalid")
        elif response.status_code == 403:
            telemetry.end_request(request_id, endpoint, False, "403")
            print(f"[DEBUG] 403 Response: {response.text}")
            raise Exception("403 Forbidden - Access denied")
        elif response.status_code == 404:
            telemetry.end_request(request_id, endpoint, False, "404")
            print(f"[DEBUG] 404 Response: {response.text}")
            raise Exception("404 Not Found")
        elif response.status_code == 429:
            telemetry.end_request(request_id, endpoint, False, "429")
            raise Exception("429 Too Many Requests - Rate limited")
        elif response.status_code >= 500:
            telemetry.end_request(request_id, endpoint, False, f"{response.status_code}")
            raise Exception(f"{response.status_code} Server Error")

    def create_video(self, account_cookie: str, prompt: str, **kwargs) -> str:
        """
        Create video via Sora API.
        PHASE 4B-1: Always shadow mode - returns mock ID without calling API.
        """
        self._check_kill_switch()
        
        # Phase 4B-1: create_video is ALWAYS shadow mode
        # This will be enabled in Phase 4B-2
        print("[SHADOW MODE] create_video - Phase 4B-1 read-only, returning mock ID")
        return f"shadow_{uuid.uuid4().hex[:8]}"

    def get_history(self, account_id: str, limit: int = 10) -> list:
        """
        Get recent video generation history.
        This is the safest read-only endpoint.
        """
        self._check_kill_switch()
        
        request_id = uuid.uuid4().hex
        telemetry.start_request(request_id)
        
        try:
            # Rate limiting
            time.sleep(config.get("rate_limit_delay", 1.0))
            
            # Sora web API endpoint for user's video history
            # This endpoint may vary - adjust based on actual observation
            response = self.session.get(
                f"{self._base_url}/api/videos",
                headers=self._get_headers(account_id),
                params={"limit": limit},
                timeout=config.get("request_timeout", 30)
            )
            
            self._handle_response_errors(response, request_id, "get_history")
            response.raise_for_status()
            
            data = response.json()
            telemetry.end_request(request_id, "get_history", True)
            
            # Return video list (structure may vary)
            if isinstance(data, list):
                return data
            return data.get("videos", data.get("items", data.get("data", [])))
            
        except requests.RequestException as e:
            telemetry.end_request(request_id, "get_history", False, "network")
            print(f"[ERROR] get_history failed: {e}")
            return []

    def get_status(self, video_id: str, account_id: str = None) -> str:
        """
        Get video generation status.
        Returns: "processing" | "completed" | "failed"
        """
        self._check_kill_switch()
        
        # Shadow mode videos
        if video_id.startswith("shadow_"):
            return "completed"

        request_id = uuid.uuid4().hex
        telemetry.start_request(request_id)
        
        try:
            # Rate limiting
            time.sleep(config.get("rate_limit_delay", 0.5))
            
            headers = self._get_headers(account_id) if account_id else {}
            
            response = self.session.get(
                f"{self._base_url}/api/videos/{video_id}",
                headers=headers,
                timeout=config.get("request_timeout", 30)
            )
            
            self._handle_response_errors(response, request_id, "get_status")
            response.raise_for_status()
            
            data = response.json()
            telemetry.end_request(request_id, "get_status", True)
            
            # Normalize status
            status = data.get("status", data.get("state", "processing"))
            if status in ["completed", "done", "finished", "ready"]:
                return "completed"
            elif status in ["failed", "error"]:
                return "failed"
            return "processing"
            
        except requests.RequestException as e:
            telemetry.end_request(request_id, "get_status", False, "network")
            raise Exception(f"get_status error: {e}")

    def download_video(self, video_id: str, path: str, account_id: str = None) -> None:
        """
        Download completed video file.
        """
        self._check_kill_switch()
        
        # Shadow mode
        if video_id.startswith("shadow_"):
            os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
            with open(path, 'w') as f:
                f.write(f"Shadow mode mock content for {video_id}")
            return

        request_id = uuid.uuid4().hex
        telemetry.start_request(request_id)
        
        try:
            headers = self._get_headers(account_id) if account_id else {}
            
            # First, get video details to find download URL
            response = self.session.get(
                f"{self._base_url}/api/videos/{video_id}",
                headers=headers,
                timeout=config.get("request_timeout", 30)
            )
            
            self._handle_response_errors(response, request_id, "download_video")
            response.raise_for_status()
            
            data = response.json()
            
            # Find video URL (structure may vary)
            video_url = (
                data.get("video_url") or 
                data.get("url") or 
                data.get("download_url") or
                data.get("media", {}).get("url")
            )
            
            if not video_url:
                telemetry.end_request(request_id, "download_video", False, "no_url")
                raise Exception("Video URL not found in response")
            
            # Download the actual video file
            video_response = self.session.get(
                video_url,
                stream=True,
                timeout=config.get("request_timeout", 120)
            )
            video_response.raise_for_status()
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
            
            with open(path, 'wb') as f:
                for chunk in video_response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            telemetry.end_request(request_id, "download_video", True)
            print(f"[OK] Downloaded video to: {path}")
            
        except requests.RequestException as e:
            telemetry.end_request(request_id, "download_video", False, "network")
            raise Exception(f"Download error: {e}")

    def is_healthy(self) -> bool:
        """Check if we have valid configuration."""
        if config.get("kill_switch", False):
            return False
        return True
