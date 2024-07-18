from datetime import datetime

from PySide2.QtCore import Signal, QThread
from PySide2.QtGui import QColor


class CopyWorker(QThread):
    update_status = Signal(int, str, QColor)
    update_total_progress = Signal(int)
    finished = Signal(bool)  # 使用布尔值表示是否完成

    def __init__(self, tcp_client, file_table, start_row=0):
        super().__init__()
        self.tcp_client = tcp_client
        self.file_table = file_table
        self._is_interrupted = False
        self._start_row = start_row

    def run(self):
        total_files = self.file_table.rowCount()
        for row in range(self._start_row, total_files):
            if self._is_interrupted:
                self.update_status.emit(row, "Interrupted", QColor("orange"))
                self._start_row = row  # 记录中断的行号
                self.finished.emit(False)  # 传递 False 表示被中断
                return

            original_path = self.file_table.item(row, 0)
            new_path = self.file_table.item(row, 1).text()
            if original_path:
                original_path = original_path.text()
                self.update_status.emit(row, "Checking...", QColor("yellow"))
                state = self.tcp_client.copy_clip(original_path, new_path)
                current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                print(state)
                print(current_time)
                if state == "copy finish":
                    result_str = "Success"
                    result_color = QColor("green")
                    self.update_status.emit(row, result_str, result_color)
                elif state == "Error: src path is not exists":
                    result_str = "Error: Path not exists"
                    result_color = QColor("red")
                    self.update_status.emit(row, result_str, result_color)
                elif state == "Warn: Target path is already exists":
                    result_str = "Path Exists"
                    result_color = QColor("yellow")
                    self.update_status.emit(row, result_str, result_color)

                self.update_total_progress.emit(int((row + 1) / total_files * 100))  # 更新总进度

        self.finished.emit(True)  # 传递 True 表示操作完成

    def interrupt(self):
        self._is_interrupted = True

    def get_start_row(self):
        return self._start_row
