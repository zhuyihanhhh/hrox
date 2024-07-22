from PySide2.QtCore import Qt
from PySide2.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QTableWidget, QAbstractItemView, QHeaderView, \
    QComboBox, QProgressBar, QVBoxLayout, QHBoxLayout, QCheckBox


class Convert_Window(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(900, 600)
        self.setStyleSheet("""
                    QWidget { font-family: Arial; }
                    QLabel { font-size: 12px; }
                    QLineEdit { font-size: 12px; }
                    QPushButton { font-size: 12px; }
                    QComboBox { font-size: 13px; }
                    QTableWidget { font-size: 12px; }
                """)
        self.init_widgets()
        self.init_layout()
        self.function_instance = None

    def init_widgets(self):
        self.setWindowTitle("Convert HROX Files")

        self.hrox_path_label = QLabel("HROX File Path:")
        self.hrox_path_lineEdit = QLineEdit("")
        self.hrox_path_button = QPushButton("...")

        self.get_path_button = QPushButton("Get Path")

        self.execute_button = QPushButton("Execute")

        self.file_table = QTableWidget(0, 3)
        self.file_table.setHorizontalHeaderLabels(["Original Path", "New Path", "Result"])
        self.file_table.setColumnWidth(2, 150)
        self.file_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.file_table.setContextMenuPolicy(Qt.CustomContextMenu)

        header = self.file_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Fixed)

        self.drives_combobox = QComboBox()
        self.drives_combobox.setMinimumSize(150, 30)

        self.interrupt_button = QPushButton("Interrupt")
        self.resume_button = QPushButton("Resume")

        self.current_fie_label = QLabel("Current File:")
        self.current_file_progress = QProgressBar()
        self.current_file_progress.setRange(0, 100)

        self.toal_files_label = QLabel("Total Progress:")
        self.total_progress = QProgressBar()
        self.total_progress.setRange(0, 100)

        self.drive_space_label = QLabel("Drive:")
        self.drive_space_label.setFixedSize(40, 30)
        self.drive_space_label.setAlignment(Qt.AlignCenter)
        self.drive_space_progress = QProgressBar()
        self.drive_space_progress.setFixedWidth(150)


        self.total_drive_space_text = QLabel()
        self.total_drive_space_text.setFixedHeight(30)
        self.total_drive_space_text.setAlignment(Qt.AlignCenter)
        self.drive_space_text = QLabel()
        self.drive_space_text.setFixedHeight(30)

        self.ip_config = QPushButton("config")


        self.send_button = QPushButton("Send")

        self.listen_checkbox = QCheckBox("Listen")
        # self.listen_checkbox.setChecked(True)
    def init_layout(self):
        main_layout = QVBoxLayout()

        hrox_path_layout = QHBoxLayout()
        hrox_path_layout.addWidget(self.hrox_path_label)
        hrox_path_layout.addWidget(self.hrox_path_lineEdit)
        hrox_path_layout.addWidget(self.hrox_path_button)

        interrupt_layout = QHBoxLayout()
        interrupt_layout.addWidget(self.interrupt_button)
        interrupt_layout.addWidget(self.resume_button)

        button_layout = QVBoxLayout()
        button_Widget = QWidget()
        button_Widget.setLayout(button_layout)
        button_Widget.setFixedWidth(200)
        button_layout.addWidget(self.ip_config)
        button_layout.addWidget(self.drives_combobox)
        button_layout.addWidget(self.get_path_button)
        button_layout.addWidget(self.execute_button)
        button_layout.addWidget(self.send_button)
        button_layout.addWidget(self.listen_checkbox)
        button_layout.addLayout(interrupt_layout)

        h_layout = QHBoxLayout()
        h_layout.addWidget(self.file_table)
        h_layout.addWidget(button_Widget)
        # h_layout.addLayout(button_layout)

        current_file_progress_layout = QHBoxLayout()
        current_file_progress_layout.addWidget(self.current_fie_label)
        current_file_progress_layout.addWidget(self.current_file_progress)

        total_files_progress_layout = QHBoxLayout()
        total_files_progress_layout.addWidget(self.toal_files_label)
        total_files_progress_layout.addWidget(self.total_progress)

        drive_space_progress_mainlayout = QVBoxLayout()

        drive_space_progress_layout = QHBoxLayout()
        drive_space_progress_layout.addWidget(self.drive_space_label)
        drive_space_progress_layout.addWidget(self.drive_space_progress)
        drive_space_text_layout = QHBoxLayout()
        drive_space_text_layout.addWidget(self.total_drive_space_text)
        drive_space_text_layout.addWidget(self.drive_space_text)
        drive_space_progress_mainlayout.addLayout(drive_space_progress_layout)
        drive_space_progress_mainlayout.addLayout(drive_space_text_layout)
        button_layout.addLayout(drive_space_progress_mainlayout)

        main_layout.addLayout(hrox_path_layout)
        main_layout.addLayout(h_layout)
        # main_layout.addLayout(current_file_progress_layout)
        main_layout.addLayout(total_files_progress_layout)
        self.setLayout(main_layout)

    def closeEvent(self, event):
        if self.function_instance and hasattr(self.function_instance, 'tcp_client'):
            print("Closing TCP connection")
            self.function_instance.tcp_client.close()
        super().closeEvent(event)
