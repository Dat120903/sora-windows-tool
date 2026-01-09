"""
Secure Auth Store - Handles cookie/session storage locally.
NO SECRETS IN CODE OR LOGS.
"""
import json
import os
from pathlib import Path
from typing import Optional, Dict
import base64

# Store in user's home directory, NOT in repo
AUTH_DIR = Path.home() / ".sora_tool" / "auth"

class SecureAuthStore:
    """
    Manages authentication credentials (cookies/tokens) for Sora accounts.
    Stores data locally in user's home directory.
    """
    
    def __init__(self):
        AUTH_DIR.mkdir(parents=True, exist_ok=True)

    def _get_path(self, account_id: str) -> Path:
        # Simple obfuscation of filename (not encryption)
        safe_id = base64.urlsafe_b64encode(account_id.encode()).decode()
        return AUTH_DIR / f"{safe_id}.json"

    def save_credentials(self, account_id: str, cookies: Dict[str, str], 
                         access_token: Optional[str] = None):
        """Save account credentials to local store."""
        data = {
            "cookies": cookies,
            "access_token": access_token,
        }
        path = self._get_path(account_id)
        with open(path, 'w') as f:
            json.dump(data, f)

    def load_credentials(self, account_id: str) -> Optional[Dict]:
        """Load account credentials from local store."""
        path = self._get_path(account_id)
        if not path.exists():
            return None
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except Exception:
            return None

    def delete_credentials(self, account_id: str):
        """Remove credentials for an account."""
        path = self._get_path(account_id)
        if path.exists():
            path.unlink()

    def get_cookie_header(self, account_id: str) -> Optional[str]:
        """Get cookie string formatted for HTTP header."""
        creds = self.load_credentials(account_id)
        if not creds or not creds.get("cookies"):
            return None
        cookies = creds["cookies"]
        return "; ".join([f"{k}={v}" for k, v in cookies.items()])

    def get_access_token(self, account_id: str) -> Optional[str]:
        """Get access token for API calls."""
        creds = self.load_credentials(account_id)
        if not creds:
            return None
        return creds.get("access_token")

# Singleton
auth_store = SecureAuthStore()
