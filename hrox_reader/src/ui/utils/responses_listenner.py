import json
import time
import socket
from PySide2.QtCore import QThread, Signal, QObject

class ServerResponseListener(QThread):
    finished_signal = Signal()
    def __init__(self, sock):
        super().__init__()
        self.sock = sock
        self.running = False

    def run(self):
        self.running = True
        while self.running:
            try:
                response = self.sock.recv(4096)
                if response:
                    state = response.decode('utf-8')
                    print(f"服务器响应: {state}")
                    if state.startswith("TargetPathIsExistsWarning"):
                        # self.update_line_signal.emit(line_number)
                        print(state)
                    elif state == "AllChunkFinish":
                        print("服务器处理完毕")
                        # self.finished_signal.emit()
                        self.running = False
                else:
                    print("未收到服务器响应")
                    self.running = False
            except socket.timeout:
                print("接收超时")
                self.running = False
            except Exception as e:
                print(f"接收服务器响应时发生错误: {e}")
                self.running = False

    def stop_listening(self):
        self.running = False
        self.wait()  # 确保线程正确停止

class FileSender(QThread):
    update_line_signal = Signal(int)
    finished_signal = Signal()

    def __init__(self, tcp_client, json_file_path):
        super().__init__()
        self.tcp_client = tcp_client
        self.json_file_path = json_file_path

    def run(self):
        self.send_file()

    def send_file(self):
        with open(self.json_file_path, "r", encoding="utf-8") as json_file:
            send_dicts = json.load(json_file)
        json_data = json.dumps(send_dicts).encode("utf-8")
        data_length = len(json_data)
        print(data_length)
        self.tcp_client.stream.sendall(str("DATA_LENGTH " + str(data_length)).encode("utf-8"))
        time.sleep(0.01)
        self.send_data_in_chunks(self.tcp_client.stream, json_data)
        print("JSON data sent successfully.")

    def send_data_in_chunks(self, sock, data, chunk_size=2048):
        # listen_thread = ServerResponseListener(sock)
        # listen_thread.start()
        start = 0
        while start < len(data):
            end = start + chunk_size
            print(b"CHUNK|" + data[start:end])
            sock.sendall(b"CHUNK|" + data[start:end])
            start = end
            time.sleep(0.1)

        # listen_thread.wait()

        self.finished_signal.emit()
# 示例调用
# 假设 tcp_client 是你的 TCP 客户端对象，并且它有一个 stream 属性代表套接字对象
# sock = tcp_client.stream  # 套接字对象
# file_sender = FileSender(tcp_client)
# data = b"your data to send"
# file_sender.send_data_in_chunks(data)
