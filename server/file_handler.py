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

    def handle_upload_start(self, file_info):
        """处理文件上传开始"""
        try:
            filename = file_info.get('filename', 'unknown')
            target_path = file_info.get('target_path', '/tmp')
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
