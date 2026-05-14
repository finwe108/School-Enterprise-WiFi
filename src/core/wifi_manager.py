from abc import ABC, abstractmethod
from typing import List, Optional
from .network_model import Network, SavedProfile
import platform


class WiFiManager(ABC):
    """Abstract base class for WiFi management across platforms."""

    @abstractmethod
    def scan_networks(self) -> List[Network]:
        """Scan for available WiFi networks."""
        pass

    @abstractmethod
    def connect(self, ssid: str, password: Optional[str] = None) -> bool:
        """Connect to a WiFi network."""
        pass

    @abstractmethod
    def disconnect(self) -> bool:
        """Disconnect from the current WiFi network."""
        pass

    @abstractmethod
    def get_current_connection(self) -> Optional[Network]:
        """Get currently connected network."""
        pass

    @abstractmethod
    def save_profile(self, profile: SavedProfile) -> bool:
        """Save a network profile."""
        pass

    @abstractmethod
    def remove_profile(self, ssid: str) -> bool:
        """Remove a saved network profile."""
        pass

    @abstractmethod
    def get_saved_profiles(self) -> List[SavedProfile]:
        """Get all saved network profiles."""
        pass

    @abstractmethod
    def forget_network(self, ssid: str) -> bool:
        """Forget a network."""
        pass

    @staticmethod
    def get_instance():
        """Factory method to get appropriate WiFiManager instance for current OS."""
        system = platform.system()
        
        if system == "Windows":
            from .windows_backend import WindowsWiFiManager
            return WindowsWiFiManager()
        elif system == "Linux":
            from .linux_backend import LinuxWiFiManager
            return LinuxWiFiManager()
        elif system == "Darwin":  # macOS
            from .macos_backend import MacOSWiFiManager
            return MacOSWiFiManager()
        else:
            raise NotImplementedError(f"WiFi management not supported on {system}")
