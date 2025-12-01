"""
客户端网络连接管理
"""
import socket
import threading
import sys
import os
import queue
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.protocol import Protocol


class ClientConnection:
    """客户端连接管理"""

    def __init__(self):
        self.socket = None
        self.connected = False
        self.receive_thread = None
        self.callbacks = {}
        # 添加文件传输消息队列
        self.file_transfer_queue = queue.Queue()
        self.uploading = False  # 标记是否正在上传
        # 添加目录列表消息队列
        self.dir_list_queue = queue.Queue()
        self.listing_dir = False  # 标记是否正在获取目录列表
        self.dir_list_lock = threading.Lock()  # 目录列表请求锁
        # 添加文件下载消息队列和状态
        self.download_queue = queue.Queue()
        self.downloading = False  # 标记是否正在下载
        self.download_lock = threading.Lock()  # 下载请求锁
        # 添加文件列表消息队列
        self.file_list_queue = queue.Queue()
        self.listing_files = False  # 标记是否正在获取文件列表
        self.file_list_lock = threading.Lock()  # 文件列表请求锁

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
            # 设置上传标志
            self.uploading = True
            # 清空队列
            while not self.file_transfer_queue.empty():
                try:
                    self.file_transfer_queue.get_nowait()
                except:
                    break

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

            # 从队列等待服务器准备好（超时10秒）
            try:
                msg_type, payload = self.file_transfer_queue.get(timeout=10)
                if msg_type != Protocol.MSG_FILE_UPLOAD or payload.get('status') != 'ready':
                    self.uploading = False
                    return False, "服务器未准备好接收文件"
            except queue.Empty:
                self.uploading = False
                return False, "等待服务器响应超时"

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

            # 从队列等待确认（超时10秒）
            try:
                msg_type, payload = self.file_transfer_queue.get(timeout=10)
                self.uploading = False
                if msg_type == Protocol.MSG_FILE_COMPLETE and payload.get('status') == 'success':
                    return True, f"文件上传成功: {payload.get('path')}"
                else:
                    return False, "文件上传失败"
            except queue.Empty:
                self.uploading = False
                return False, "等待服务器确认超时"

        except Exception as e:
            self.uploading = False
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

    def list_dir(self, path='/'):
        """获取远程目录列表"""
        if not self.connected:
            return None, "未连接到服务器"

        # 使用锁确保一次只有一个目录列表请求
        with self.dir_list_lock:
            try:
                print(f"[DEBUG] 开始请求目录列表: {path}")
                # 设置列表标志
                self.listing_dir = True
                # 清空队列
                while not self.dir_list_queue.empty():
                    try:
                        self.dir_list_queue.get_nowait()
                    except:
                        break

                # 发送目录列表请求
                msg = Protocol.pack_message(Protocol.MSG_LIST_DIR, {'path': path})
                self.socket.send(msg)
                print(f"[DEBUG] 已发送目录列表请求，等待响应...")

                # 从队列等待响应（超时10秒，增加超时时间）
                try:
                    msg_type, payload = self.dir_list_queue.get(timeout=10)
                    print(f"[DEBUG] 收到响应: msg_type={msg_type}, payload={payload}")
                    self.listing_dir = False
                    if msg_type == Protocol.MSG_LIST_DIR:
                        return payload, None
                    elif msg_type == Protocol.MSG_ERROR:
                        return None, payload.get('error', '未知错误')
                    else:
                        return None, "响应格式错误"
                except queue.Empty:
                    self.listing_dir = False
                    print(f"[DEBUG] 等待响应超时！listing_dir={self.listing_dir}")
                    return None, "等待服务器响应超时"

            except Exception as e:
                self.listing_dir = False
                print(f"[DEBUG] 异常: {e}")
                return None, f"获取目录列表失败: {str(e)}"

    def list_files(self, path='/'):
        """获取远程文件和文件夹列表"""
        if not self.connected:
            return None, "未连接到服务器"

        with self.file_list_lock:
            try:
                print(f"[DEBUG] 开始请求文件列表: {path}")
                # 设置列表标志
                self.listing_files = True
                # 清空队列
                while not self.file_list_queue.empty():
                    try:
                        self.file_list_queue.get_nowait()
                    except:
                        break

                # 发送文件列表请求
                msg = Protocol.pack_message(Protocol.MSG_FILE_LIST, {'path': path})
                self.socket.send(msg)
                print(f"[DEBUG] 已发送文件列表请求，等待响应...")

                # 从队列等待响应（超时10秒）
                try:
                    msg_type, payload = self.file_list_queue.get(timeout=10)
                    print(f"[DEBUG] 收到响应: msg_type={msg_type}")
                    self.listing_files = False
                    if msg_type == Protocol.MSG_FILE_LIST and payload.get('status') == 'success':
                        return payload, None
                    elif msg_type == Protocol.MSG_ERROR:
                        return None, payload.get('error', '未知错误')
                    else:
                        return None, "响应格式错误"
                except queue.Empty:
                    self.listing_files = False
                    print(f"[DEBUG] 等待文件列表响应超时！")
                    return None, "等待服务器响应超时"

            except Exception as e:
                self.listing_files = False
                print(f"[DEBUG] 获取文件列表异常: {e}")
                return None, f"获取文件列表失败: {str(e)}"

    def download_file(self, remote_file_path, local_save_path):
        """下载文件"""
        if not self.connected:
            return False, "未连接到服务器"

        with self.download_lock:
            try:
                # 设置下载标志
                self.downloading = True
                # 清空队列
                while not self.download_queue.empty():
                    try:
                        self.download_queue.get_nowait()
                    except:
                        break

                print(f"[DEBUG] 开始下载文件: {remote_file_path}")

                # 发送文件下载请求
                msg = Protocol.pack_message(
                    Protocol.MSG_FILE_DOWNLOAD,
                    {'file_path': remote_file_path}
                )
                self.socket.send(msg)

                # 等待服务器准备好（超时10秒）
                try:
                    msg_type, payload = self.download_queue.get(timeout=10)
                    if msg_type == Protocol.MSG_ERROR:
                        self.downloading = False
                        return False, payload.get('error', '下载失败')
                    if msg_type != Protocol.MSG_FILE_DOWNLOAD or payload.get('status') != 'ready':
                        self.downloading = False
                        return False, "服务器未准备好发送文件"
                except queue.Empty:
                    self.downloading = False
                    return False, "等待服务器响应超时"

                # 获取文件信息
                filename = payload.get('filename', 'download')
                file_size = payload.get('size', 0)

                print(f"[DEBUG] 开始接收文件数据: {filename}, 大小: {file_size}")

                # 准备保存文件
                received_size = 0
                with open(local_save_path, 'wb') as f:
                    # 接收文件数据
                    while True:
                        try:
                            msg_type, payload = self.download_queue.get(timeout=30)

                            if msg_type == Protocol.MSG_FILE_DATA:
                                # 写入数据块
                                if isinstance(payload, bytes):
                                    f.write(payload)
                                    received_size += len(payload)
                                elif isinstance(payload, dict) and 'data' in payload:
                                    import base64
                                    data = base64.b64decode(payload['data'])
                                    f.write(data)
                                    received_size += len(data)

                                # 调用进度回调
                                if 'file_progress' in self.callbacks:
                                    progress = (received_size / file_size * 100) if file_size > 0 else 0
                                    self.callbacks['file_progress'](progress, received_size, file_size)

                            elif msg_type == Protocol.MSG_FILE_COMPLETE:
                                # 文件传输完成
                                print(f"[DEBUG] 文件下载完成: {received_size} 字节")
                                self.downloading = False
                                if payload.get('status') == 'success':
                                    return True, f"文件下载成功: {local_save_path}"
                                else:
                                    return False, "文件下载失败"

                            elif msg_type == Protocol.MSG_ERROR:
                                self.downloading = False
                                return False, payload.get('error', '下载失败')

                        except queue.Empty:
                            self.downloading = False
                            return False, "接收文件数据超时"

            except Exception as e:
                self.downloading = False
                print(f"[DEBUG] 下载文件异常: {e}")
                return False, f"下载文件失败: {str(e)}"

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

                # 打印收到的消息类型（用于调试）
                if msg_type == Protocol.MSG_LIST_DIR:
                    print(f"[DEBUG] 接收循环收到 MSG_LIST_DIR 消息, listing_dir={self.listing_dir}")
                elif msg_type not in (Protocol.MSG_TERMINAL_OUTPUT, Protocol.MSG_HEARTBEAT):
                    print(f"[DEBUG] 接收循环收到消息: msg_type={msg_type}")

                # 文件传输相关消息 - 放入队列
                if self.uploading and msg_type in (Protocol.MSG_FILE_UPLOAD, Protocol.MSG_FILE_COMPLETE, Protocol.MSG_ERROR):
                    self.file_transfer_queue.put((msg_type, payload))

                # 文件下载相关消息 - 放入队列
                elif self.downloading and msg_type in (Protocol.MSG_FILE_DOWNLOAD, Protocol.MSG_FILE_DATA, Protocol.MSG_FILE_COMPLETE, Protocol.MSG_ERROR):
                    self.download_queue.put((msg_type, payload))

                # 目录列表相关消息 - 放入队列
                elif self.listing_dir and msg_type in (Protocol.MSG_LIST_DIR, Protocol.MSG_ERROR):
                    print(f"[DEBUG] 接收到目录列表消息: msg_type={msg_type}, listing_dir={self.listing_dir}")
                    self.dir_list_queue.put((msg_type, payload))

                # 文件列表相关消息 - 放入队列
                elif self.listing_files and msg_type in (Protocol.MSG_FILE_LIST, Protocol.MSG_ERROR):
                    print(f"[DEBUG] 接收到文件列表消息: msg_type={msg_type}")
                    self.file_list_queue.put((msg_type, payload))

                # 终端输出
                elif msg_type == Protocol.MSG_TERMINAL_OUTPUT:
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
