from dataclasses import dataclass
from typing import Optional
from enum import Enum


class SecurityType(Enum):
    OPEN = "Open"
    WEP = "WEP"
    WPA = "WPA"
    WPA2 = "WPA2"
    WPA3 = "WPA3"
    UNKNOWN = "Unknown"


@dataclass
class Network:
    """Represents a WiFi network."""
    ssid: str
    signal_strength: int  # 0-100 percentage
    security: SecurityType
    frequency: Optional[str] = None
    channel: Optional[int] = None
    bssid: Optional[str] = None
    ip_address: Optional[str] = None
    is_connected: bool = False

    def __str__(self):
        return f"{self.ssid} ({self.signal_strength}%) - {self.security.value}"


@dataclass
class SavedProfile:
    """Represents a saved WiFi network profile."""
    ssid: str
    security: SecurityType
    auto_connect: bool = False
    last_connected: Optional[str] = None
    connection_count: int = 0

    def __str__(self):
        return f"{self.ssid} ({'Auto' if self.auto_connect else 'Manual'})"
