import socket


class ReviewClient():
    def __init__(self, ip, port):
        super().__init__()
        self.ip = ip
        self.port = port
        self.stream = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.stream.connect((self.ip, self.port))
            # connect_status = self._check_connection()
            # if not connect_status:
            #     raise ConnectionError('TCP连接失败')
            # print(connect_status)
        except (socket.timeout, ConnectionError) as e:
            print(f'连接失败: {e}')
        finally:
            pass

    # def _check_connection(self) -> bool:
    #     try:
    #         self.stream.send('get_connection'.encode('utf-8'))
    #         data = self.stream.recv(1024)
    #         if not data:
    #             return False
    #         connect_status = data.decode('utf-8')
    #         return connect_status
    #     except socket.timeout:
    #         return False

    @property
    def get_drivers(self):
        key_word = 'get_driver'
        self.stream.send(key_word.encode('utf-8'))
        while True:
            data = self.stream.recv(4096)
            if not data:
                break
            else:
                drivers = data.decode('utf-8')
                # print(drivers)
                return drivers

    # def send_clip(self):
    #     paths = self.file_path
    #     for path in paths:
    #         if " " in path:
    #             print(f"{path}有空格，请修改路径")
    #         else:
    #             if os.path.exists(path):
    #                 if os.path.isdir(path):
    #                     self.stream.send(path.encode('utf-8'))
    #                 else:
    #                     self.stream.send(path.encode('utf-8'))
    #             else:
    #                 print(f"{path}不存在")

    def copy_clip(self, clip_path, new_path):
        cp_command = f'cp {clip_path} {new_path}'
        self.stream.send(cp_command.encode('utf-8'))
        print(cp_command)
        # time.sleep(0.1)
        data = self.stream.recv(4096)
        if not data:
            pass
        else:
            state = data.decode('utf-8')

            return state

    def close(self):
        self.stream.close()

    @property
    def get_drive_space(self):
        _command = 'get_free_space'
        self.stream.send(_command.encode('utf-8'))
        data = self.stream.recv(4096)
        if not data:
            pass
        else:
            state = data.decode('utf-8')
            return state