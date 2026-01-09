"""
Cookie Import Utility - Parses JSON cookie exports from Cookie-Editor extension.
SECURITY: Never logs cookie values.
"""
import json
from pathlib import Path
from typing import Dict, List, Optional

# Required cookies for Sora authentication
REQUIRED_COOKIES = [
    "__Secure-next-auth.session-token",
]

# Cookies to capture (auth-related)
AUTH_COOKIE_PATTERNS = [
    "__Secure-next-auth",
    "__Host-next-auth",
    "__cf_bm",
    "cf_clearance",
    "_cfuvid",
]

def parse_cookie_editor_json(file_path: str) -> Dict[str, str]:
    """
    Parse JSON export from Cookie-Editor browser extension.
    
    Expected format (array of cookie objects):
    [
        {
            "name": "__Secure-next-auth.session-token",
            "value": "...",
            "domain": ".sora.com",
            ...
        },
        ...
    ]
    
    Returns: Dict of cookie name -> value (sora.com cookies only)
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Cookie file not found: {file_path}")
    
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if not isinstance(data, list):
        raise ValueError("Expected JSON array of cookie objects")
    
    cookies = {}
    for cookie in data:
        if not isinstance(cookie, dict):
            continue
        
        name = cookie.get("name", "")
        value = cookie.get("value", "")
        domain = cookie.get("domain", "")
        
        # Filter: Only sora.com cookies
        if not _is_sora_domain(domain):
            continue
        
        # Filter: Only auth-related cookies
        if not _is_auth_cookie(name):
            continue
        
        if name and value:
            cookies[name] = value
    
    return cookies


def validate_cookies(cookies: Dict[str, str]) -> List[str]:
    """
    Validate that required cookies are present.
    Returns list of missing required cookies.
    """
    missing = []
    for required in REQUIRED_COOKIES:
        if required not in cookies:
            missing.append(required)
    return missing


def _is_sora_domain(domain: str) -> bool:
    """Check if domain is sora.com or .sora.com"""
    domain = domain.lower().strip()
    return domain in ["sora.com", ".sora.com", "www.sora.com"]


def _is_auth_cookie(name: str) -> bool:
    """Check if cookie name matches auth-related patterns."""
    for pattern in AUTH_COOKIE_PATTERNS:
        if pattern in name:
            return True
    return False


def get_cookie_summary(cookies: Dict[str, str]) -> str:
    """
    Get a safe summary of cookies (no values logged).
    """
    lines = ["Imported cookies:"]
    for name in sorted(cookies.keys()):
        # Show name and value length only (NEVER the actual value)
        value_len = len(cookies[name])
        lines.append(f"  - {name}: {value_len} chars")
    return "\n".join(lines)
