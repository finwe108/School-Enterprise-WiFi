import subprocess
import re
from typing import List, Optional
from .wifi_manager import WiFiManager
from .network_model import Network, SavedProfile, SecurityType


class LinuxWiFiManager(WiFiManager):
    """WiFi manager for Linux systems using nmcli (NetworkManager)."""

    def scan_networks(self) -> List[Network]:
        """Scan for available WiFi networks on Linux."""
        networks = []
        try:
            result = subprocess.run(
                ["nmcli", "dev", "wifi", "list"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            lines = result.stdout.strip().split('\n')
            if len(lines) > 1:
                for line in lines[1:]:
                    parts = re.split(r'\s{2,}', line.strip())
                    if len(parts) >= 8:
                        ssid = parts[1]
                        signal = int(parts[5])
                        security = parts[7]
                        
                        security_type = self._parse_security(security)
                        network = Network(
                            ssid=ssid,
                            signal_strength=signal,
                            security=security_type
                        )
                        
                        if not any(n.ssid == network.ssid for n in networks):
                            networks.append(network)
        except Exception as e:
            print(f"Error scanning networks: {e}")
        
        return networks

    def connect(self, ssid: str, password: Optional[str] = None) -> bool:
        """Connect to a WiFi network on Linux."""
        try:
            if password:
                result = subprocess.run(
                    ["nmcli", "device", "wifi", "connect", ssid, "password", password],
                    capture_output=True,
                    text=True,
                    timeout=15
                )
            else:
                result = subprocess.run(
                    ["nmcli", "device", "wifi", "connect", ssid],
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
                ["nmcli", "device", "disconnect", "wifi"],
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
                ["nmcli", "connection", "show", "--active"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            for line in result.stdout.split('\n'):
                if "connection.type" in line and "802-11-wireless" in line:
                    # Found WiFi connection
                    result2 = subprocess.run(
                        ["nmcli", "-t", "dev", "wifi", "list"],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    
                    lines = result2.stdout.strip().split('\n')
                    for line in lines:
                        parts = line.split(':')
                        if len(parts) >= 3 and "yes" in parts[0]:
                            ssid = parts[1]
                            return Network(
                                ssid=ssid,
                                signal_strength=50,
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
                ["nmcli", "connection", "delete", ssid],
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
                ["nmcli", "connection", "show"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            for line in result.stdout.split('\n'):
                if "TYPE" in line and "802-11-wireless" in line:
                    parts = line.split()
                    if len(parts) > 0:
                        ssid = parts[0]
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
        """Parse security type from nmcli output."""
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
