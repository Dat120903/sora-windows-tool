"""
Abstract interface for Sora Client implementations.
Both MockSoraClient and SoraApiAdapter must implement this interface.
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

class SoraClientInterface(ABC):
    """
    Abstract base class defining the contract for Sora API clients.
    This allows swapping between Mock and Real implementations without
    modifying the Core Engine.
    """
    
    @abstractmethod
    def create_video(self, account_cookie: str, prompt: str, **kwargs) -> str:
        """
        Create a video generation request.
        Returns: external_sora_id (str)
        Raises: Exception on error (401, 429, network, etc.)
        """
        pass

    @abstractmethod
    def get_status(self, video_id: str) -> str:
        """
        Get the status of a video generation.
        Returns: "processing" | "finished" | "failed"
        """
        pass

    @abstractmethod
    def download_video(self, video_id: str, path: str) -> None:
        """
        Download the finished video to local path.
        Raises: Exception if video not ready or download fails.
        """
        pass

    @abstractmethod
    def get_history(self, account_cookie: str, limit: int = 5) -> list:
        """
        Get recent video generation history for idempotency checks.
        Returns: List of recent video metadata dicts.
        """
        pass

    def is_healthy(self) -> bool:
        """
        Health check for the client. Default: True.
        Override for real API to check connectivity.
        """
        return True
