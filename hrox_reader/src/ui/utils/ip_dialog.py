from PySide2.QtCore import Qt
from PySide2.QtWidgets import QDialog, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout


class IPPortDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("config")
        self.setModal(True)

        self.init_widget()
        self.init_layout()
        self.init_connection()

    def init_widget(self):
        self.ip_label = QLabel(" IP :")
        self.ip_label.setFixedWidth(30)
        self.ip_label.setAlignment(Qt.AlignRight)
        self.ip_input = QLineEdit("127.0.0.1")
        self.port_label = QLabel(" Port:")
        self.port_label.setFixedWidth(30)
        self.port_label.setAlignment(Qt.AlignRight)
        self.port_input = QLineEdit("8075")

        self.ok_button = QPushButton("OK")
        self.cancel_button = QPushButton("Cancel")

    def init_layout(self):
        layout = QVBoxLayout()
        ip_layout = QHBoxLayout()
        ip_layout.addWidget(self.ip_label)
        ip_layout.addWidget(self.ip_input)
        layout.addLayout(ip_layout)

        port_layout = QHBoxLayout()
        port_layout.addWidget(self.port_label)
        port_layout.addWidget(self.port_input)
        layout.addLayout(port_layout)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def init_connection(self):
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

    def get_ip_port(self):
        return self.ip_input.text(), int(self.port_input.text())

    def set_defaults(self, ip, port):
        self.ip_input.setText(ip)
        self.port_input.setText(str(port))
