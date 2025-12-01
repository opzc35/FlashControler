"""
Linux服务端主程序
处理客户端连接、终端执行、文件接收
"""
import socket
import threading
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.protocol import Protocol
from common.config import Config
from common.version import __version__, UPDATE_URL
from server.terminal_handler import TerminalHandler
from server.file_handler import FileHandler
from server.ip_blacklist import IPBlacklist


class FlashServer:
    """FlashControler服务端"""

    def __init__(self, config_file="config/settings.json"):
        self.config = Config(config_file)
        self.host = self.config.get('server', 'host', '0.0.0.0')
        self.port = self.config.get('server', 'port', 9999)
        self.password = self.config.get('server', 'password', 'flashcontrol123')

        # IP黑名单管理器
        self.ip_blacklist = IPBlacklist()

        self.server_socket = None
        self.clients = []
        self.running = False

    def start(self):
        """启动服务器"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            self.running = True

            print(f"[FlashControler] 服务器启动成功")
            print(f"[FlashControler] 监听地址: {self.host}:{self.port}")
            print(f"[FlashControler] 等待客户端连接...")

            while self.running:
                try:
                    client_socket, client_address = self.server_socket.accept()
                    print(f"[FlashControler] 新连接来自: {client_address}")

                    # 为每个客户端创建处理线程
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, client_address)
                    )
                    client_thread.daemon = True
                    client_thread.start()

                except Exception as e:
                    if self.running:
                        print(f"[错误] 接受连接失败: {e}")

        except Exception as e:
            print(f"[错误] 服务器启动失败: {e}")
        finally:
            self.stop()

    def handle_client(self, client_socket, client_address):
        """处理客户端连接"""
        client_ip = client_address[0]  # 提取IP地址
        authenticated = False
        terminal_handler = None
        file_handler = None

        try:
            # 检查IP是否被封锁
            is_blocked, block_reason = self.ip_blacklist.check_blocked(client_ip)
            if is_blocked:
                print(f"[安全] ❌ IP {client_ip} 已被封锁，拒绝连接")
                print(f"[安全]    封锁原因: {block_reason}")
                # 发送拒绝消息后立即关闭连接
                try:
                    response = Protocol.pack_message(Protocol.MSG_AUTH, {
                        "status": "blocked",
                        "reason": block_reason
                    })
                    client_socket.send(response)
                except:
                    pass
                return

            # 等待认证
            msg_type, payload = Protocol.receive_message(client_socket)

            if msg_type == Protocol.MSG_AUTH:
                if payload == self.password:
                    authenticated = True
                    response = Protocol.pack_message(Protocol.MSG_AUTH, {"status": "success"})
                    client_socket.send(response)

                    # 记录认证成功
                    self.ip_blacklist.record_auth_success(client_ip)
                    print(f"[认证] ✓ IP {client_ip} 认证成功")

                    # 初始化处理器
                    terminal_handler = TerminalHandler(client_socket)
                    file_handler = FileHandler(client_socket)
                else:
                    response = Protocol.pack_message(Protocol.MSG_AUTH, {"status": "failed"})
                    client_socket.send(response)

                    # 记录认证失败
                    auto_blocked = self.ip_blacklist.record_auth_failure(client_ip)
                    status = self.ip_blacklist.blacklist.get(client_ip, {})
                    fail_count = status.get('fail_count', 0)

                    print(f"[认证] ✗ IP {client_ip} 认证失败 (失败次数: {fail_count}/{self.ip_blacklist.max_failures})")

                    if auto_blocked:
                        print(f"[安全] 🔒 IP {client_ip} 已自动封锁（认证失败{fail_count}次）")
                        print(f"[安全]    使用 'python unlock_ip.py {client_ip}' 解锁")

                    return

            if not authenticated:
                return

            # 处理客户端消息
            while self.running:
                msg_type, payload = Protocol.receive_message(client_socket)

                if msg_type is None:
                    print(f"[FlashControler] 客户端 {client_address} 断开连接")
                    break

                # 终端输入
                if msg_type == Protocol.MSG_TERMINAL_INPUT:
                    terminal_handler.handle_input(payload)

                # 文件上传
                elif msg_type == Protocol.MSG_FILE_UPLOAD:
                    file_handler.handle_upload_start(payload)

                # 文件数据
                elif msg_type == Protocol.MSG_FILE_DATA:
                    file_handler.handle_file_data(payload)

                # 文件传输完成
                elif msg_type == Protocol.MSG_FILE_COMPLETE:
                    file_handler.handle_upload_complete()

                # 更新检查
                elif msg_type == Protocol.MSG_UPDATE_CHECK:
                    self.handle_update_check(client_socket)

                # 列出目录（只返回目录）
                elif msg_type == Protocol.MSG_LIST_DIR:
                    self.handle_list_dir(client_socket, payload)

                # 文件列表（返回文件和目录）
                elif msg_type == Protocol.MSG_FILE_LIST:
                    file_handler.handle_file_list_request(payload)

                # 文件下载
                elif msg_type == Protocol.MSG_FILE_DOWNLOAD:
                    file_handler.handle_download_request(payload)

                # 心跳包
                elif msg_type == Protocol.MSG_HEARTBEAT:
                    response = Protocol.pack_message(Protocol.MSG_HEARTBEAT, "pong")
                    client_socket.send(response)

        except Exception as e:
            print(f"[错误] 处理客户端 {client_address} 时出错: {e}")
        finally:
            if terminal_handler:
                terminal_handler.stop()
            client_socket.close()
            print(f"[FlashControler] 客户端 {client_address} 连接已关闭")

    def handle_update_check(self, client_socket):
        """处理更新检查"""
        # 版本号和更新URL现在从代码中获取，不再从配置文件读取
        # 配置文件中的 update_url 可以覆盖默认值
        update_url = self.config.get('update', 'update_url', UPDATE_URL)

        response = Protocol.pack_message(Protocol.MSG_UPDATE_INFO, {
            "current_version": __version__,
            "update_url": update_url
        })
        client_socket.send(response)

    def handle_list_dir(self, client_socket, payload):
        """处理目录列表请求"""
        try:
            path = payload.get('path', '/') if isinstance(payload, dict) else '/'

            # 确保路径存在且是目录
            if not os.path.exists(path):
                response = Protocol.pack_message(Protocol.MSG_ERROR, {
                    "error": "路径不存在"
                })
                client_socket.send(response)
                return

            if not os.path.isdir(path):
                response = Protocol.pack_message(Protocol.MSG_ERROR, {
                    "error": "不是目录"
                })
                client_socket.send(response)
                return

            # 获取目录内容
            items = []
            try:
                for item_name in sorted(os.listdir(path)):
                    item_path = os.path.join(path, item_name)
                    try:
                        is_dir = os.path.isdir(item_path)
                        # 只添加目录，不添加文件
                        if is_dir:
                            items.append({
                                'name': item_name,
                                'path': item_path,
                                'is_dir': True
                            })
                    except PermissionError:
                        # 跳过没有权限的目录
                        continue
            except PermissionError:
                response = Protocol.pack_message(Protocol.MSG_ERROR, {
                    "error": "权限不足"
                })
                client_socket.send(response)
                return

            # 发送目录列表
            response = Protocol.pack_message(Protocol.MSG_LIST_DIR, {
                "path": path,
                "items": items
            })
            client_socket.send(response)

        except Exception as e:
            print(f"[错误] 列出目录失败: {e}")
            response = Protocol.pack_message(Protocol.MSG_ERROR, {
                "error": str(e)
            })
            client_socket.send(response)

    def stop(self):
        """停止服务器"""
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        print("[FlashControler] 服务器已停止")


def main():
    """主函数"""
    server = FlashServer()
    try:
        server.start()
    except KeyboardInterrupt:
        print("\n[FlashControler] 收到中断信号，正在关闭服务器...")
        server.stop()


if __name__ == '__main__':
    main()
