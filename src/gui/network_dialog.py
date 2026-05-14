from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton
from PyQt6.QtCore import Qt
from ..core.network_model import Network, SecurityType


class ConnectDialog(QDialog):
    """Dialog for entering password and connecting to a network."""
    
    def __init__(self, network: Network, parent=None):
        super().__init__(parent)
        self.network = network
        self.password = ""
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the dialog UI."""
        self.setWindowTitle(f"Connect to {self.network.ssid}")
        self.setModal(True)
        self.setGeometry(200, 200, 400, 150)
        
        layout = QVBoxLayout()
        
        # Network info
        info_label = QLabel(f"Network: {self.network.ssid}")
        layout.addWidget(info_label)
        
        security_label = QLabel(f"Security: {self.network.security.value}")
        layout.addWidget(security_label)
        
        # Password input (only if network requires authentication)
        if self.network.security != SecurityType.OPEN:
            password_label = QLabel("Password:")
            layout.addWidget(password_label)
            
            self.password_input = QLineEdit()
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
            layout.addWidget(self.password_input)
        else:
            self.password_input = None
            no_password_label = QLabel("This is an open network. No password required.")
            layout.addWidget(no_password_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        connect_btn = QPushButton("Connect")
        connect_btn.clicked.connect(self.accept)
        button_layout.addWidget(connect_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def accept(self):
        """Accept and capture password."""
        if self.password_input:
            self.password = self.password_input.text()
        super().accept()
