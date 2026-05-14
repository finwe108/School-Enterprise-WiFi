import sys
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QListWidget, QListWidgetItem, QLabel, QProgressBar, QTabWidget, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QIcon, QFont, QColor
from typing import List
from ..core.wifi_manager import WiFiManager
from ..core.network_model import Network, SavedProfile
from ..storage.database import WiFiDatabase
from .network_dialog import ConnectDialog


class ScanWorker(QThread):
    """Worker thread for scanning WiFi networks without blocking UI."""
    scan_complete = pyqtSignal(list)
    error_occurred = pyqtSignal(str)
    
    def run(self):
        try:
            manager = WiFiManager.get_instance()
            networks = manager.scan_networks()
            self.scan_complete.emit(networks)
        except Exception as e:
            self.error_occurred.emit(str(e))


class WiFiManagerUI(QMainWindow):
    """Main GUI window for WiFi Manager."""
    
    def __init__(self):
        super().__init__()
        self.manager = WiFiManager.get_instance()
        self.db = WiFiDatabase()
        self.scan_worker = None
        
        self.init_ui()
        self.setup_auto_refresh()
        self.initial_scan()
    
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("WiFi Manager")
        self.setGeometry(100, 100, 800, 600)
        
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Create tab widget
        tabs = QTabWidget()
        layout.addWidget(tabs)
        
        # Networks tab
        networks_tab = QWidget()
        networks_layout = QVBoxLayout()
        
        # Title
        title = QLabel("Available Networks")
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title.setFont(title_font)
        networks_layout.addWidget(title)
        
        # Network list
        self.network_list = QListWidget()
        self.network_list.itemClicked.connect(self.on_network_selected)
        networks_layout.addWidget(self.network_list)
        
        # Current connection status
        self.status_label = QLabel("Status: Not connected")
        networks_layout.addWidget(self.status_label)
        
        # Button panel
        button_layout = QHBoxLayout()
        
        self.scan_btn = QPushButton("🔄 Scan Networks")
        self.scan_btn.clicked.connect(self.scan_networks)
        button_layout.addWidget(self.scan_btn)
        
        self.connect_btn = QPushButton("⚡ Connect")
        self.connect_btn.clicked.connect(self.on_connect_clicked)
        self.connect_btn.setEnabled(False)
        button_layout.addWidget(self.connect_btn)
        
        self.disconnect_btn = QPushButton("🔌 Disconnect")
        self.disconnect_btn.clicked.connect(self.disconnect_network)
        button_layout.addWidget(self.disconnect_btn)
        
        networks_layout.addLayout(button_layout)
        networks_tab.setLayout(networks_layout)
        tabs.addTab(networks_tab, "Networks")
        
        # Saved profiles tab
        profiles_tab = QWidget()
        profiles_layout = QVBoxLayout()
        
        title2 = QLabel("Saved Profiles")
        title2.setFont(title_font)
        profiles_layout.addWidget(title2)
        
        self.profiles_list = QListWidget()
        self.profiles_list.itemClicked.connect(self.on_profile_selected)
        profiles_layout.addWidget(self.profiles_list)
        
        # Profile buttons
        profile_btn_layout = QHBoxLayout()
        
        self.add_profile_btn = QPushButton("➕ Add Profile")
        self.add_profile_btn.clicked.connect(self.add_profile)
        self.add_profile_btn.setEnabled(False)
        profile_btn_layout.addWidget(self.add_profile_btn)
        
        self.remove_profile_btn = QPushButton("❌ Remove Profile")
        self.remove_profile_btn.clicked.connect(self.remove_profile)
        self.remove_profile_btn.setEnabled(False)
        profile_btn_layout.addWidget(self.remove_profile_btn)
        
        self.autoconnect_btn = QPushButton("🔄 Toggle Auto-Connect")
        self.autoconnect_btn.clicked.connect(self.toggle_autoconnect)
        self.autoconnect_btn.setEnabled(False)
        profile_btn_layout.addWidget(self.autoconnect_btn)
        
        profiles_layout.addLayout(profile_btn_layout)
        profiles_tab.setLayout(profiles_layout)
        tabs.addTab(profiles_tab, "Saved Profiles")
        
        self.load_profiles()
    
    def scan_networks(self):
        """Scan for available WiFi networks."""
        self.scan_btn.setEnabled(False)
        self.scan_btn.setText("Scanning...")
        
        self.scan_worker = ScanWorker()
        self.scan_worker.scan_complete.connect(self.display_networks)
        self.scan_worker.error_occurred.connect(self.show_error)
        self.scan_worker.start()
    
    def display_networks(self, networks: List[Network]):
        """Display scanned networks in the list."""
        self.network_list.clear()
        
        for network in networks:
            item_text = f"{network.ssid} ({network.signal_strength}%) - {network.security.value}"
            item = QListWidgetItem(item_text)
            
            # Color code by signal strength
            if network.signal_strength >= 70:
                item.setForeground(QColor("green"))
            elif network.signal_strength >= 40:
                item.setForeground(QColor("orange"))
            else:
                item.setForeground(QColor("red"))
            
            item.setData(Qt.ItemDataRole.UserRole, network)
            self.network_list.addItem(item)
        
        self.scan_btn.setEnabled(True)
        self.scan_btn.setText("🔄 Scan Networks")
        self.update_status()
    
    def on_network_selected(self, item):
        """Handle network selection."""
        self.connect_btn.setEnabled(True)
    
    def on_connect_clicked(self):
        """Open connection dialog."""
        current_item = self.network_list.currentItem()
        if not current_item:
            return
        
        network: Network = current_item.data(Qt.ItemDataRole.UserRole)
        
        dialog = ConnectDialog(network, self)
        if dialog.exec():
            self.connect_to_network(network.ssid, dialog.password)
    
    def connect_to_network(self, ssid: str, password: str = ""):
        """Connect to a network."""
        try:
            password_arg = password if password else None
            success = self.manager.connect(ssid, password_arg)
            
            if success:
                self.db.record_connection(ssid, True)
                self.show_info(f"Successfully connected to {ssid}")
                self.update_status()
            else:
                self.show_error(f"Failed to connect to {ssid}")
        except Exception as e:
            self.show_error(f"Error: {e}")
    
    def disconnect_network(self):
        """Disconnect from current network."""
        try:
            success = self.manager.disconnect()
            if success:
                self.show_info("Disconnected successfully")
                self.update_status()
            else:
                self.show_error("Failed to disconnect")
        except Exception as e:
            self.show_error(f"Error: {e}")
    
    def update_status(self):
        """Update connection status."""
        try:
            current = self.manager.get_current_connection()
            if current:
                self.status_label.setText(f"Status: Connected to {current.ssid} ({current.signal_strength}%)")
            else:
                self.status_label.setText("Status: Not connected")
        except Exception as e:
            self.status_label.setText("Status: Unknown")
    
    def load_profiles(self):
        """Load and display saved profiles."""
        self.profiles_list.clear()
        profiles = self.db.get_all_profiles()
        
        for profile in profiles:
            auto_text = " ✓" if profile.auto_connect else ""
            item_text = f"{profile.ssid}{auto_text}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, profile)
            self.profiles_list.addItem(item)
    
    def on_profile_selected(self, item):
        """Handle profile selection."""
        self.remove_profile_btn.setEnabled(True)
        self.autoconnect_btn.setEnabled(True)
    
    def add_profile(self):
        """Add current network to saved profiles."""
        current_item = self.network_list.currentItem()
        if not current_item:
            self.show_error("Please select a network first")
            return
        
        network: Network = current_item.data(Qt.ItemDataRole.UserRole)
        
        try:
            profile = SavedProfile(
                ssid=network.ssid,
                security=network.security,
                auto_connect=False
            )
            
            if self.db.add_profile(profile):
                self.show_info(f"Profile saved for {network.ssid}")
                self.load_profiles()
            else:
                self.show_error(f"Profile already exists for {network.ssid}")
        except Exception as e:
            self.show_error(f"Error: {e}")
    
    def remove_profile(self):
        """Remove a saved profile."""
        current_item = self.profiles_list.currentItem()
        if not current_item:
            return
        
        profile: SavedProfile = current_item.data(Qt.ItemDataRole.UserRole)
        
        if QMessageBox.question(self, "Confirm", f"Remove profile for {profile.ssid}?") == QMessageBox.StandardButton.Yes:
            try:
                self.db.delete_profile(profile.ssid)
                self.manager.forget_network(profile.ssid)
                self.show_info(f"Profile removed for {profile.ssid}")
                self.load_profiles()
            except Exception as e:
                self.show_error(f"Error: {e}")
    
    def toggle_autoconnect(self):
        """Toggle auto-connect for a profile."""
        current_item = self.profiles_list.currentItem()
        if not current_item:
            return
        
        profile: SavedProfile = current_item.data(Qt.ItemDataRole.UserRole)
        
        try:
            profile.auto_connect = not profile.auto_connect
            self.db.update_profile(profile)
            self.load_profiles()
            status = "enabled" if profile.auto_connect else "disabled"
            self.show_info(f"Auto-connect {status} for {profile.ssid}")
        except Exception as e:
            self.show_error(f"Error: {e}")
    
    def setup_auto_refresh(self):
        """Setup auto-refresh timer for network status."""
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.update_status)
        self.refresh_timer.start(5000)  # Refresh every 5 seconds
    
    def initial_scan(self):
        """Perform initial network scan."""
        self.scan_networks()
    
    def show_error(self, message: str):
        """Show error message."""
        QMessageBox.critical(self, "Error", message)
    
    def show_info(self, message: str):
        """Show info message."""
        QMessageBox.information(self, "Info", message)


def run_gui():
    """Run the GUI application."""
    app = __import__('PyQt6.QtWidgets', fromlist=['QApplication']).QApplication(sys.argv)
    window = WiFiManagerUI()
    window.show()
    sys.exit(app.exec())
