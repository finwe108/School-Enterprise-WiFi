# WiFi Manager

A cross-platform WiFi management tool with both CLI and GUI interfaces.

## Features

- **Scan Networks**: List all available WiFi networks with signal strength and security type
- **Connect/Disconnect**: Connect to networks with password support
- **Manage Profiles**: Save and manage WiFi network profiles
- **Auto-Connect**: Set networks to connect automatically
- **Connection History**: Track connection statistics
- **Cross-Platform**: Works on Windows, Linux, and macOS
- **Dual Interface**: Use via command-line or graphical interface

## Installation

### Requirements
- Python 3.9 or higher
- pip

### Setup

1. Clone or download this project:
```bash
cd wifi-manager
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

Or use setup.py:
```bash
pip install -e .
```

## Usage

### Graphical Interface

Launch the GUI:
```bash
python -m src.main gui
```

Features:
- Network list with signal strength visualization
- One-click connect/disconnect
- Saved profiles management
- Connection status display

### Command-Line Interface

#### Scan networks
```bash
python -m src.main cli scan
```

#### Connect to a network
```bash
python -m src.main cli connect "NetworkName"
# Enter password when prompted
```

#### Disconnect
```bash
python -m src.main cli disconnect
```

#### Show current status
```bash
python -m src.main cli status
```

#### List saved profiles
```bash
python -m src.main cli list-saved
```

#### Save a network profile
```bash
python -m src.main cli add-profile "NetworkName"
```

#### Remove a saved profile
```bash
python -m src.main cli remove-profile "NetworkName"
```

#### Toggle auto-connect
```bash
python -m src.main cli toggle-autoconnect "NetworkName"
```

## Platform-Specific Notes

### Windows
- Uses `netsh` command for WiFi operations
- Requires administrator privileges for connecting/disconnecting
- Profiles are managed by Windows

### Linux
- Requires NetworkManager (`nmcli` command)
- Install: `sudo apt install network-manager`
- May require sudo for some operations

### macOS
- Uses `networksetup` and `airport` commands
- Requires administrator privileges
- Works with standard WiFi interface (en0)

## Saved Profiles

Profiles are stored in SQLite database located at:
- **Linux/macOS**: `~/.wifi_manager/profiles.db`
- **Windows**: `%USERPROFILE%\.wifi_manager\profiles.db`

Each profile stores:
- Network SSID
- Security type
- Auto-connect setting
- Connection history
- Last connection time

## Troubleshooting

### Permission Denied
On Linux/macOS, you may need sudo for certain operations:
```bash
sudo python -m src.main cli scan
```

### Network Not Found
Ensure WiFi is enabled on your device and try scanning again.

### Connection Failed
- Verify the network SSID and password are correct
- Check that your WiFi adapter is working
- Try disconnecting and reconnecting

## License

MIT License

## Contributing

Contributions welcome! Please fork and submit pull requests.
