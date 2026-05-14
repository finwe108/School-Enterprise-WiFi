import subprocess
import re
from typing import List, Optional
from .wifi_manager import WiFiManager
from .network_model import Network, SavedProfile, SecurityType


class WindowsWiFiManager(WiFiManager):
    """WiFi manager for Windows systems using netsh commands."""

    def scan_networks(self) -> List[Network]:
        """Scan for available WiFi networks on Windows."""
        networks = []
        try:
            result = subprocess.run(
                ["netsh", "wlan", "show", "networks", "mode=Bssid"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            current_ssid = None
            signal_strength = 0
            security = None
            
            for line in result.stdout.split('\n'):
                if "SSID" in line and ":" in line:
                    parts = line.split(":", 1)
                    if len(parts) > 1:
                        current_ssid = parts[1].strip()
                
                if "Signal" in line and "%" in line:
                    match = re.search(r'(\d+)%', line)
                    if match:
                        signal_strength = int(match.group(1))
                
                if "Authentication" in line and ":" in line:
                    parts = line.split(":", 1)
                    if len(parts) > 1:
                        auth_type = parts[1].strip().upper()
                        if "WPA3" in auth_type:
                            security = SecurityType.WPA3
                        elif "WPA2" in auth_type:
                            security = SecurityType.WPA2
                        elif "WPA" in auth_type:
                            security = SecurityType.WPA
                        elif "WEP" in auth_type:
                            security = SecurityType.WEP
                        elif "Open" in auth_type:
                            security = SecurityType.OPEN
                        else:
                            security = SecurityType.UNKNOWN
                
                if current_ssid and signal_strength and security:
                    network = Network(
                        ssid=current_ssid,
                        signal_strength=signal_strength,
                        security=security
                    )
                    # Avoid duplicates
                    if not any(n.ssid == network.ssid for n in networks):
                        networks.append(network)
                    current_ssid = None
                    signal_strength = 0
                    security = None
                    
        except Exception as e:
            print(f"Error scanning networks: {e}")
        
        return networks

    def connect(self, ssid: str, password: Optional[str] = None) -> bool:
        """Connect to a WiFi network on Windows."""
        try:
            if password:
                # Create XML profile
                profile_xml = self._create_profile_xml(ssid, password)
                # Add profile
                subprocess.run(
                    ["netsh", "wlan", "add", "profile", f"filename={profile_xml}"],
                    capture_output=True,
                    timeout=10
                )
            
            # Connect to network
            result = subprocess.run(
                ["netsh", "wlan", "connect", f"name={ssid}"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            return "successfully" in result.stdout.lower() or result.returncode == 0
        except Exception as e:
            print(f"Error connecting to network: {e}")
            return False

    def disconnect(self) -> bool:
        """Disconnect from current network."""
        try:
            result = subprocess.run(
                ["netsh", "wlan", "disconnect"],
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
                ["netsh", "wlan", "show", "interfaces"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            ssid = None
            signal = 0
            
            for line in result.stdout.split('\n'):
                if "SSID" in line and ":" in line:
                    parts = line.split(":", 1)
                    if len(parts) > 1:
                        ssid = parts[1].strip()
                
                if "Signal" in line and "%" in line:
                    match = re.search(r'(\d+)%', line)
                    if match:
                        signal = int(match.group(1))
            
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
        # Windows automatically saves profiles when connected
        return True

    def remove_profile(self, ssid: str) -> bool:
        """Remove a saved profile."""
        try:
            result = subprocess.run(
                ["netsh", "wlan", "delete", "profile", f"name={ssid}"],
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
                ["netsh", "wlan", "show", "profiles"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            for line in result.stdout.split('\n'):
                if "All User Profile" in line and ":" in line:
                    parts = line.split(":", 1)
                    if len(parts) > 1:
                        ssid = parts[1].strip()
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
    def _create_profile_xml(ssid: str, password: str) -> str:
        """Create a WiFi profile XML for Windows."""
        xml_content = f"""<?xml version="1.0"?>
<WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
    <name>{ssid}</name>
    <SSIDConfig>
        <SSID>
            <hex>{ssid.encode().hex()}</hex>
            <name>{ssid}</name>
        </SSID>
    </SSIDConfig>
    <connectionType>ESS</connectionType>
    <connectionMode>auto</connectionMode>
    <MSM>
        <security>
            <authEncryption>
                <authentication>WPA2PSK</authentication>
                <encryption>CCMP</encryption>
                <useOneX>false</useOneX>
            </authEncryption>
            <sharedKey>
                <keyType>passPhrase</keyType>
                <protected>false</protected>
                <keyMaterial>{password}</keyMaterial>
            </sharedKey>
        </security>
    </MSM>
</WLANProfile>"""
        return xml_content
