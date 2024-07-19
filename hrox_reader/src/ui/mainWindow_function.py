import json
import os
import re
import socket
import subprocess
import sys
import time
from datetime import datetime

from PySide2.QtCore import Qt
from PySide2.QtWidgets import QTableWidgetItem, QMessageBox, QApplication, QFileDialog, QMenu, QAction, QDialog

from tcp_connect import ReviewClient as RC
from ui.utils.CopyWorker import CopyWorker as copy
from ui.utils.info_widget import NotificationWidget as info
from ui.utils.ip_dialog import IPPortDialog as ip_dialog
from ui.utils.responses_listenner import ServerResponseListener as rl, FileSender


class mainWindow_function():
    def __init__(self, mainWindow):
        self.clip_pattern = re.compile(r'file="([A-Z]:[^"]+)"')
        self._start_row = 0

        self.ipd = ip_dialog(mainWindow)
        if self.ipd.exec_() == QDialog.Accepted:
            ip, port = self.ipd.get_ip_port()
        else:
            sys.exit()

        self.tcp_client = RC(ip, port)
        # self.listener = rl(self.tcp_client.stream)

        self.window = mainWindow
        self.window.function_instance = self
        self.connect_signals()
        # self.show_drive_space()

    def show_info(self, title, message):
        new_notification = info(title, message)

    def connect_signals(self):

        # self.listener.update_line_signal.connect(self.on_update_line)
        # self.listener.finished_signal.connect(self.on_finished)

        self.window.get_path_button.clicked.connect(self.set_paths)
        # self.window.execute_button.clicked.connect(self.set_operation_result)
        self.window.hrox_path_button.clicked.connect(self.open_file_dialog)
        self.window.interrupt_button.clicked.connect(self.interrupt_copy)
        self.window.resume_button.clicked.connect(self.resume_copy)
        self.window.file_table.customContextMenuRequested.connect(self.show_context_menu)
        self.window.ip_config.clicked.connect(self.modify_connection)
        self.get_drivers()
        self.window.send_button.clicked.connect(self.test_slot)

        self.window.listen_checkbox.stateChanged.connect(self.toggle_listen_server_responses)

    def show_context_menu(self, position):
        menu = QMenu()

        open_file_action = QAction("打开当前文件", self.window)
        open_file_action.triggered.connect(self.open_file)
        menu.addAction(open_file_action)

        open_folder_action = QAction("打开文件所在文件夹", self.window)
        open_folder_action.triggered.connect(self.open_folder)
        menu.addAction(open_folder_action)

        menu.exec_(self.window.file_table.viewport().mapToGlobal(position))

    def open_file(self):
        current_item = self.window.file_table.currentItem()
        if current_item:
            # row = self.window.file_table.currentRow()
            file_path = current_item.text()  # 假设文件路径在第2列
            if os.path.exists(file_path):
                subprocess.Popen(['start', file_path],
                                 shell=True)  # 使用默认程序打开文件（Windows: 'start', macOS: 'open', Linux: 'xdg-open'）
            else:
                QMessageBox.warning(self.window, "Warning", "File do not exists: " + file_path)

    def open_folder(self):
        current_item = self.window.file_table.currentItem()
        if current_item:
            # row = self.window.file_table.currentRow()
            file_path = current_item.text().replace("/", "\\")
            folder_path = os.path.dirname(file_path)
            if os.path.exists(folder_path):
                subprocess.Popen(['start', folder_path],
                                 shell=True)  # 使用默认文件管理器打开文件夹（Windows: 'explorer', macOS: 'open', Linux: 'xdg-open'）
            else:
                QMessageBox.warning(self.window, "Warning", "Folder do not exists: " + file_path)

    def resume_copy(self):
        if hasattr(self, 'worker') and not self.worker.isRunning():
            self.set_operation_result()

    def interrupt_copy(self):
        if hasattr(self, 'worker') and self.worker.isRunning():
            self.worker.interrupt()
            self._start_row = self.worker.get_start_row()

    def result(self, file_path):
        return os.path.isdir(file_path)

    def open_file_dialog(self):
        # 打开文件选择对话框
        file_path, _ = QFileDialog.getOpenFileName(self.window, "Select HROX File", "", "HROX Files (*.hrox)")

        if file_path:
            # 设置文件路径到 QLineEdit
            self.window.hrox_path_lineEdit.setText(file_path)

    def set_operation_result(self):
        if self.window.file_table.rowCount() == 0:
            QMessageBox.warning(self.window, "提示", "表格中没有内容。")
            return

        self.worker = copy(self.tcp_client, self.window.file_table, self._start_row)
        self.worker.update_status.connect(self.update_table)
        self.worker.update_total_progress.connect(self.window.total_progress.setValue)
        self.worker.finished.connect(self.on_operation_finished)
        self.worker.start()

    def update_table(self, row, status, color):
        item = QTableWidgetItem(status)
        item.setBackground(color)
        self.window.file_table.setItem(row, 2, item)
        self.window.file_table.scrollToItem(item)
        self.window.file_table.repaint()
        QApplication.processEvents()

    def on_operation_finished(self, completed):
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if completed:
            title = f"Operation Result {current_time}"
            message = "All operations have been completed."
            self.show_info(title, message)
            self._start_row = 0
        else:
            self._start_row = self.worker.get_start_row()
            title = "Interrupted"
            message = "Copy operation has been interrupted."
            self.show_info(title, message)

    def set_paths(self):
        paths = self.file_path

        self.window.file_table.clearContents()
        self.window.file_table.setRowCount(0)

        for path in paths:
            row_position = self.window.file_table.rowCount()
            self.window.file_table.insertRow(row_position)
            self.window.file_table.setItem(row_position, 0, QTableWidgetItem(path))
            new_path = self.local_path(path)
            self.window.file_table.setItem(row_position, 1, QTableWidgetItem(new_path))
            self.window.file_table.setItem(row_position, 2, QTableWidgetItem("Waiting..."))

    def local_path(self, path):
        new_drive = self.window.drives_combobox.currentText().split(":")[0]
        parts = path.split(':')
        if len(parts) > 1:
            return new_drive + ":" + parts[1]
        else:
            pass

    def is_path_in_table(self, path):
        for row in range(self.window.file_table.rowCount()):
            item = self.window.file_table.item(row, 0)
            if item and item.text() == path:
                return True
        return False

    def get_drivers(self):
        # 获取盘符列表
        # drivers = self.drivers
        drivers = []
        if not drivers:
            drivers = ["C:/"]
            self.window.drives_combobox.addItems(drivers)
        else:
            # 将盘符加入到 QComboBox 中
            self.window.drives_combobox.clear()  # 清空之前的内容
            self.window.drives_combobox.addItems(drivers)

    @property
    def drivers(self):
        drivers = self.tcp_client.get_drivers.replace("Driver:", "").split("|")
        print(drivers)
        return drivers

    @property
    def file_path(self):
        with open(self.window.hrox_path_lineEdit.text(), 'r', encoding='utf-8') as file:
            file_content = file.read()

        clip_paths = self.clip_pattern.findall(file_content)

        paths = []
        for i in clip_paths:
            dir_name = os.path.dirname(i)
            if os.path.exists(dir_name):
                if ".dpx" in i:
                    dir_path = os.path.dirname(i)
                    paths.append(dir_path)
                    # pass
                else:
                    paths.append(i)
        return paths

    @property
    def drive_space(self):
        return self.tcp_client.get_drive_space

    def modify_connection(self):
        current_ip = self.tcp_client.ip
        current_port = self.tcp_client.port
        self.ipd.set_defaults(current_ip, current_port)

        if self.ipd.exec_() == QDialog.Accepted:
            ip, port = self.ipd.get_ip_port()
            self.tcp_client.close()
            self.tcp_client = RC(ip, port)
            QMessageBox.information(self.window, "连接信息", f"已连接到 {ip}:{port}")
        else:
            pass

    def show_drive_space(self):
        value = self.drive_space
        print(value)

        available_space = value.split(" ")[-1].split(":")[-1]
        total_space = value.split(" ")[-2].split(":")[-1]

        # 转换为TB
        available_space_tb = float(available_space) / (1024 ** 4)
        total_space_tb = float(total_space) / (1024 ** 4)

        ratio = available_space_tb / total_space_tb
        self.window.drive_space_progress.setValue(int((1 - ratio) * 100))

        available_space_tb_text = round(available_space_tb, 2)
        total_space_tb_text = round(total_space_tb, 2)
        self.window.total_drive_space_text.setText(f"总容量:{total_space_tb_text} TB")
        self.window.drive_space_text.setText(f"可用:{available_space_tb_text} TB")

    # def send_file(self):
    #     with open(self.json_file_path, "r", encoding="utf-8") as json_file:
    #         send_dicts = json.load(json_file)
    #     # 将整个文件内容作为JSON字符串
    #     json_data = json.dumps(send_dicts).encode("utf-8")
    #     # 发送JSON数据的长度
    #     data_length = len(json_data)
    #     print(data_length)
    #     self.tcp_client.stream.sendall(str("DATA_LENGTH " + str(data_length)).encode("utf-8"))
    #     time.sleep(0.01)
    #
    #     # 分块发送JSON数据a
    #     self.send_data_in_chunks(self.tcp_client.stream, json_data)
    #     print("JSON data sent successfully.")
    def send_file_in_thread(self):
        self.file_sender = FileSender(self.tcp_client, self.json_file_path)
        self.file_sender.update_line_signal.connect(self.on_update_line)
        self.file_sender.finished_signal.connect(self.on_finished)
        self.file_sender.start()

    def export_to_json(self, file_name):
        data = []
        for row in range(self.window.file_table.rowCount()):
            row_data = {}
            item_src = self.window.file_table.item(row, 0)
            item_target = self.window.file_table.item(row, 1)
            row_data['src'] = item_src.text() if item_src else ''
            if item_target:
                target_path = item_target.text().replace("\\\\", "//").replace("\\", "/")
            else:
                target_path = ''
            row_data['target'] = target_path
            data.append(row_data)

        with open(file_name, "w+", encoding="utf-8") as file:
            json.dump(data, file)

        print(f"表格内容已导出到 {file_name}")

    def test_slot(self):
        hrox_base_name = os.path.basename(self.window.hrox_path_lineEdit.text())
        json_file_name = os.path.splitext(hrox_base_name)[0] + "_taskconfig.json"
        self.json_file_path = os.path.join(os.path.dirname(self.window.hrox_path_lineEdit.text()), json_file_name)
        self.export_to_json(self.json_file_path)
        self.send_file_in_thread()

    # def send_data_in_chunks(self, sock, data, chunk_size=2048):
    #     listener = rl(sock)
    #     listener.start()
    #     start = 0
    #     while start < len(data):
    #         end = start + chunk_size
    #         print(b"CHUNK|" + data[start: end])
    #         sock.sendall(b"CHUNK|" + data[start:end])
    #         start = end
    #         time.sleep(0.1)  # 添加小的延时
    #
    #
    #     listener.wait()

    def on_update_line(self, line):
        pass

    def on_finished(self):
        print("服务器处理完毕")

    def toggle_listen_server_responses(self, state):
        if state == Qt.Checked:
            self.start_listening()
        else:
            self.stop_listening()

    def start_listening(self):
        self.listener = rl(self.tcp_client.stream)
        # self.listener.update_line_signal.connect(self.on_update_line)
        self.listener.finished_signal.connect(self.on_finished)
        self.listener.start()

    def stop_listening(self):
        if hasattr(self, 'listener'):
            self.listener.stop_listening()
