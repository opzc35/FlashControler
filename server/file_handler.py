"""
文件处理器
处理文件接收和存储
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.protocol import Protocol


class FileHandler:
    """文件处理器"""

    def __init__(self, client_socket):
        self.client_socket = client_socket
        self.current_file = None
        self.current_file_path = None
        self.total_size = 0
        self.received_size = 0
        self.chunk_size = 65536  # 64KB 块大小，优化传输速度

    def handle_upload_start(self, file_info):
        """处理文件上传开始"""
        try:
            filename = file_info.get('filename') or 'unknown'
            target_path = file_info.get('target_path') or '/tmp'
            self.total_size = file_info.get('size', 0)
            self.received_size = 0

            # 确保目标目录存在
            os.makedirs(target_path, exist_ok=True)

            # 构建完整文件路径
            self.current_file_path = os.path.join(target_path, filename)

            # 打开文件准备写入
            self.current_file = open(self.current_file_path, 'wb')

            print(f"[文件传输] 开始接收文件: {filename}")
            print(f"[文件传输] 目标路径: {self.current_file_path}")
            print(f"[文件传输] 文件大小: {self.total_size} 字节")

            # 发送确认
            response = Protocol.pack_message(
                Protocol.MSG_FILE_UPLOAD,
                {"status": "ready"}
            )
            self.client_socket.send(response)

        except Exception as e:
            print(f"[错误] 准备接收文件失败: {e}")
            response = Protocol.pack_message(
                Protocol.MSG_ERROR,
                {"error": str(e)}
            )
            self.client_socket.send(response)

    def handle_file_data(self, data):
        """处理文件数据"""
        try:
            if self.current_file is None:
                print("[错误] 没有正在接收的文件")
                return

            # 如果data是字典，提取实际的数据
            if isinstance(data, dict):
                data = data.get('data', b'')
                if isinstance(data, str):
                    # Base64解码或其他处理
                    import base64
                    data = base64.b64decode(data)

            # 写入文件
            self.current_file.write(data)
            self.received_size += len(data)

            # 打印进度
            progress = (self.received_size / self.total_size * 100) if self.total_size > 0 else 0
            print(f"[文件传输] 接收进度: {progress:.1f}% ({self.received_size}/{self.total_size})")

        except Exception as e:
            print(f"[错误] 写入文件数据失败: {e}")

    def handle_upload_complete(self):
        """处理文件上传完成"""
        try:
            if self.current_file:
                self.current_file.close()
                print(f"[文件传输] 文件接收完成: {self.current_file_path}")
                print(f"[文件传输] 总计接收: {self.received_size} 字节")

                # 发送完成确认
                response = Protocol.pack_message(
                    Protocol.MSG_FILE_COMPLETE,
                    {
                        "status": "success",
                        "path": self.current_file_path,
                        "size": self.received_size
                    }
                )
                self.client_socket.send(response)

                # 重置状态
                self.current_file = None
                self.current_file_path = None
                self.total_size = 0
                self.received_size = 0

        except Exception as e:
            print(f"[错误] 完成文件接收失败: {e}")
            response = Protocol.pack_message(
                Protocol.MSG_ERROR,
                {"error": str(e)}
            )
            self.client_socket.send(response)

    def handle_download_request(self, file_info):
        """处理文件下载请求"""
        try:
            file_path = file_info.get('file_path') if isinstance(file_info, dict) else file_info

            # 验证文件路径
            if not file_path:
                raise ValueError("文件路径不能为空")

            # 检查文件是否存在
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"文件不存在: {file_path}")

            # 检查是否是文件（不是目录）
            if not os.path.isfile(file_path):
                raise ValueError(f"不是有效的文件: {file_path}")

            # 获取文件信息
            file_size = os.path.getsize(file_path)
            filename = os.path.basename(file_path)

            print(f"[文件下载] 开始发送文件: {filename}")
            print(f"[文件下载] 文件路径: {file_path}")
            print(f"[文件下载] 文件大小: {file_size} 字节")

            # 发送文件元数据
            response = Protocol.pack_message(
                Protocol.MSG_FILE_DOWNLOAD,
                {
                    "status": "ready",
                    "filename": filename,
                    "size": file_size,
                    "path": file_path
                }
            )
            self.client_socket.send(response)

            # 发送文件数据
            sent_size = 0
            with open(file_path, 'rb') as f:
                while True:
                    chunk = f.read(self.chunk_size)
                    if not chunk:
                        break

                    # 发送数据块
                    data_msg = Protocol.pack_message(Protocol.MSG_FILE_DATA, chunk)
                    self.client_socket.send(data_msg)

                    sent_size += len(chunk)
                    progress = (sent_size / file_size * 100) if file_size > 0 else 0
                    print(f"[文件下载] 发送进度: {progress:.1f}% ({sent_size}/{file_size})")

            # 发送完成消息
            complete_msg = Protocol.pack_message(
                Protocol.MSG_FILE_COMPLETE,
                {
                    "status": "success",
                    "filename": filename,
                    "size": sent_size
                }
            )
            self.client_socket.send(complete_msg)

            print(f"[文件下载] 文件发送完成: {filename}")
            print(f"[文件下载] 总计发送: {sent_size} 字节")

        except FileNotFoundError as e:
            print(f"[错误] 文件不存在: {e}")
            response = Protocol.pack_message(
                Protocol.MSG_ERROR,
                {"error": f"文件不存在: {str(e)}"}
            )
            self.client_socket.send(response)

        except PermissionError as e:
            print(f"[错误] 权限不足: {e}")
            response = Protocol.pack_message(
                Protocol.MSG_ERROR,
                {"error": f"权限不足: {str(e)}"}
            )
            self.client_socket.send(response)

        except Exception as e:
            print(f"[错误] 文件下载失败: {e}")
            response = Protocol.pack_message(
                Protocol.MSG_ERROR,
                {"error": str(e)}
            )
            self.client_socket.send(response)

    def handle_file_list_request(self, path_info):
        """处理文件列表请求（包含文件和文件夹）"""
        try:
            path = path_info.get('path', '/') if isinstance(path_info, dict) else path_info

            # 确保路径存在且是目录
            if not os.path.exists(path):
                raise FileNotFoundError(f"路径不存在: {path}")

            if not os.path.isdir(path):
                raise ValueError(f"不是目录: {path}")

            # 获取目录内容（文件和文件夹）
            items = []
            try:
                for item_name in sorted(os.listdir(path)):
                    item_path = os.path.join(path, item_name)
                    try:
                        is_dir = os.path.isdir(item_path)
                        size = 0 if is_dir else os.path.getsize(item_path)

                        items.append({
                            'name': item_name,
                            'path': item_path,
                            'is_dir': is_dir,
                            'size': size
                        })
                    except (PermissionError, OSError):
                        # 跳过没有权限或无法访问的项
                        continue

            except PermissionError:
                raise PermissionError(f"权限不足: {path}")

            # 发送文件列表
            response = Protocol.pack_message(
                Protocol.MSG_FILE_LIST,
                {
                    "status": "success",
                    "path": path,
                    "items": items
                }
            )
            self.client_socket.send(response)

            print(f"[文件列表] 已发送目录内容: {path} ({len(items)} 项)")

        except (FileNotFoundError, ValueError, PermissionError) as e:
            print(f"[错误] 获取文件列表失败: {e}")
            response = Protocol.pack_message(
                Protocol.MSG_ERROR,
                {"error": str(e)}
            )
            self.client_socket.send(response)

        except Exception as e:
            print(f"[错误] 处理文件列表请求失败: {e}")
            response = Protocol.pack_message(
                Protocol.MSG_ERROR,
                {"error": str(e)}
            )
            self.client_socket.send(response)
