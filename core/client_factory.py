"""
Client Factory - Creates the appropriate Sora client based on config.
This is the ONLY place that decides Mock vs Real API.
"""
from .config import config
from .sora_client_interface import SoraClientInterface
from .mock_sora_client import MockSoraClient
from .sora_api_adapter import SoraApiAdapter

def create_sora_client() -> SoraClientInterface:
    """
    Factory function to create the appropriate Sora client.
    Respects feature flags and kill-switch.
    
    Returns:
        MockSoraClient if use_real_api=False or kill_switch=True
        SoraApiAdapter if use_real_api=True
    """
    if config.use_real_api:
        print("[INFO] Using REAL Sora API Adapter")
        if config.is_shadow_mode:
            print("[INFO] Shadow mode ENABLED - create_video will be mocked")
        return SoraApiAdapter()
    else:
        print("[INFO] Using Mock Sora Client")
        return MockSoraClient()
