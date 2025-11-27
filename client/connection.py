"""
客户端网络连接管理
"""
import socket
import threading
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.protocol import Protocol


class ClientConnection:
    """客户端连接管理"""

    def __init__(self):
        self.socket = None
        self.connected = False
        self.receive_thread = None
        self.callbacks = {}

    def connect(self, host, port, password):
        """连接到服务器"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(10)
            self.socket.connect((host, port))

            # 发送认证
            auth_msg = Protocol.pack_message(Protocol.MSG_AUTH, password)
            self.socket.send(auth_msg)

            # 等待认证响应
            msg_type, payload = Protocol.receive_message(self.socket)

            if msg_type == Protocol.MSG_AUTH and payload.get('status') == 'success':
                self.connected = True
                self.socket.settimeout(None)

                # 启动接收线程
                self.receive_thread = threading.Thread(target=self._receive_loop)
                self.receive_thread.daemon = True
                self.receive_thread.start()

                return True, "连接成功"
            else:
                return False, "认证失败"

        except socket.timeout:
            return False, "连接超时"
        except Exception as e:
            return False, f"连接失败: {str(e)}"

    def disconnect(self):
        """断开连接"""
        self.connected = False
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        self.socket = None

    def send_terminal_input(self, command):
        """发送终端输入"""
        if not self.connected:
            return False

        try:
            msg = Protocol.pack_message(Protocol.MSG_TERMINAL_INPUT, command)
            self.socket.send(msg)
            return True
        except Exception as e:
            print(f"发送终端输入失败: {e}")
            self.connected = False
            return False

    def upload_file(self, file_path, target_path):
        """上传文件"""
        if not self.connected:
            return False, "未连接到服务器"

        try:
            # 获取文件信息
            filename = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)

            # 发送文件上传请求
            file_info = {
                'filename': filename,
                'target_path': target_path,
                'size': file_size
            }
            msg = Protocol.pack_message(Protocol.MSG_FILE_UPLOAD, file_info)
            self.socket.send(msg)

            # 等待服务器准备好
            msg_type, payload = Protocol.receive_message(self.socket)
            if msg_type != Protocol.MSG_FILE_UPLOAD or payload.get('status') != 'ready':
                return False, "服务器未准备好接收文件"

            # 读取并发送文件数据
            with open(file_path, 'rb') as f:
                sent_size = 0
                while True:
                    chunk = f.read(8192)
                    if not chunk:
                        break

                    # 发送数据块
                    import base64
                    data_msg = Protocol.pack_message(
                        Protocol.MSG_FILE_DATA,
                        {'data': base64.b64encode(chunk).decode('ascii')}
                    )
                    self.socket.send(data_msg)

                    sent_size += len(chunk)

                    # 调用进度回调
                    if 'file_progress' in self.callbacks:
                        progress = (sent_size / file_size * 100) if file_size > 0 else 0
                        self.callbacks['file_progress'](progress, sent_size, file_size)

            # 发送完成消息
            complete_msg = Protocol.pack_message(Protocol.MSG_FILE_COMPLETE, {})
            self.socket.send(complete_msg)

            # 等待确认
            msg_type, payload = Protocol.receive_message(self.socket)
            if msg_type == Protocol.MSG_FILE_COMPLETE and payload.get('status') == 'success':
                return True, f"文件上传成功: {payload.get('path')}"
            else:
                return False, "文件上传失败"

        except Exception as e:
            return False, f"上传文件失败: {str(e)}"

    def check_update(self):
        """检查更新"""
        if not self.connected:
            return None

        try:
            msg = Protocol.pack_message(Protocol.MSG_UPDATE_CHECK, {})
            self.socket.send(msg)
            return True
        except Exception as e:
            print(f"检查更新失败: {e}")
            return False

    def register_callback(self, event, callback):
        """注册回调函数"""
        self.callbacks[event] = callback

    def _receive_loop(self):
        """接收循环"""
        while self.connected:
            try:
                msg_type, payload = Protocol.receive_message(self.socket)

                if msg_type is None:
                    print("连接已断开")
                    self.connected = False
                    if 'disconnected' in self.callbacks:
                        self.callbacks['disconnected']()
                    break

                # 终端输出
                if msg_type == Protocol.MSG_TERMINAL_OUTPUT:
                    if 'terminal_output' in self.callbacks:
                        self.callbacks['terminal_output'](payload)

                # 更新信息
                elif msg_type == Protocol.MSG_UPDATE_INFO:
                    if 'update_info' in self.callbacks:
                        self.callbacks['update_info'](payload)

                # 错误消息
                elif msg_type == Protocol.MSG_ERROR:
                    if 'error' in self.callbacks:
                        self.callbacks['error'](payload)

            except Exception as e:
                if self.connected:
                    print(f"接收消息失败: {e}")
                    self.connected = False
                    if 'disconnected' in self.callbacks:
                        self.callbacks['disconnected']()
                break

        print("接收线程已停止")
