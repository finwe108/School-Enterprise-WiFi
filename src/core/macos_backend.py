import subprocess
import re
from typing import List, Optional
from .wifi_manager import WiFiManager
from .network_model import Network, SavedProfile, SecurityType


class MacOSWiFiManager(WiFiManager):
    """WiFi manager for macOS systems using airport command."""

    def scan_networks(self) -> List[Network]:
        """Scan for available WiFi networks on macOS."""
        networks = []
        try:
            result = subprocess.run(
                ["/System/Library/PrivateFrameworks/Apple80211.framework/Resources/airport", "-s"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            for line in result.stdout.strip().split('\n')[1:]:
                parts = re.split(r'\s{2,}', line.strip())
                if len(parts) >= 7:
                    ssid = parts[0]
                    bssid = parts[1]
                    signal = int(parts[2])
                    channel = int(parts[3].split(',')[0])
                    security = parts[6]
                    
                    signal_strength = min(100, max(0, (signal + 100)))
                    security_type = self._parse_security(security)
                    
                    network = Network(
                        ssid=ssid,
                        signal_strength=signal_strength,
                        security=security_type,
                        channel=channel,
                        bssid=bssid
                    )
                    
                    if not any(n.ssid == network.ssid for n in networks):
                        networks.append(network)
        except Exception as e:
            print(f"Error scanning networks: {e}")
        
        return networks

    def connect(self, ssid: str, password: Optional[str] = None) -> bool:
        """Connect to a WiFi network on macOS."""
        try:
            if password:
                result = subprocess.run(
                    ["networksetup", "-setairportnetwork", "en0", ssid, password],
                    capture_output=True,
                    text=True,
                    timeout=15
                )
            else:
                result = subprocess.run(
                    ["networksetup", "-setairportnetwork", "en0", ssid],
                    capture_output=True,
                    text=True,
                    timeout=15
                )
            
            return result.returncode == 0
        except Exception as e:
            print(f"Error connecting to network: {e}")
            return False

    def disconnect(self) -> bool:
        """Disconnect from current network."""
        try:
            result = subprocess.run(
                ["networksetup", "-setairportpower", "en0", "off"],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except Exception as e:
            print(f"Error disconnecting: {e}")
            return False

    def get_current_connection(self) -> Optional[Network]:
        """Get currently connected network."""
        try:
            result = subprocess.run(
                ["/System/Library/PrivateFrameworks/Apple80211.framework/Resources/airport", "-I"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            ssid = None
            signal = 0
            
            for line in result.stdout.split('\n'):
                if "SSID" in line:
                    parts = line.split(":", 1)
                    if len(parts) > 1:
                        ssid = parts[1].strip()
                
                if "agrCtlRSSI" in line:
                    match = re.search(r'-(\d+)', line)
                    if match:
                        signal = min(100, max(0, 100 + int(match.group(1))))
            
            if ssid and ssid != "":
                return Network(
                    ssid=ssid,
                    signal_strength=signal,
                    security=SecurityType.UNKNOWN,
                    is_connected=True
                )
        except Exception as e:
            print(f"Error getting current connection: {e}")
        
        return None

    def save_profile(self, profile: SavedProfile) -> bool:
        """Save a network profile."""
        return True

    def remove_profile(self, ssid: str) -> bool:
        """Remove a saved profile."""
        try:
            result = subprocess.run(
                ["networksetup", "-removepreferredwirelessnetwork", "en0", ssid],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except Exception as e:
            print(f"Error removing profile: {e}")
            return False

    def get_saved_profiles(self) -> List[SavedProfile]:
        """Get all saved network profiles."""
        profiles = []
        try:
            result = subprocess.run(
                ["networksetup", "-listpreferredwirelessnetworks", "en0"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            for line in result.stdout.split('\n')[1:]:
                ssid = line.strip()
                if ssid:
                    profiles.append(SavedProfile(
                        ssid=ssid,
                        security=SecurityType.UNKNOWN
                    ))
        except Exception as e:
            print(f"Error getting saved profiles: {e}")
        
        return profiles

    def forget_network(self, ssid: str) -> bool:
        """Forget a network."""
        return self.remove_profile(ssid)

    @staticmethod
    def _parse_security(security_str: str) -> SecurityType:
        """Parse security type from airport output."""
        if "WPA3" in security_str:
            return SecurityType.WPA3
        elif "WPA2" in security_str:
            return SecurityType.WPA2
        elif "WPA" in security_str:
            return SecurityType.WPA
        elif "WEP" in security_str:
            return SecurityType.WEP
        elif "Open" in security_str or security_str.strip() == "":
            return SecurityType.OPEN
        return SecurityType.UNKNOWN
