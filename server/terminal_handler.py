"""
终端处理器
处理远程终端的输入输出
支持UTF-8编码，正确显示中文
"""
import os
import pty
import select
import subprocess
import threading
import sys
import locale

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.protocol import Protocol


class TerminalHandler:
    """终端处理器"""

    def __init__(self, client_socket):
        self.client_socket = client_socket
        self.master_fd = None
        self.slave_fd = None
        self.process = None
        self.running = False
        self.output_thread = None

        self.start_terminal()

    def start_terminal(self):
        """启动终端"""
        try:
            # 创建伪终端
            self.master_fd, self.slave_fd = pty.openpty()

            # 设置环境变量，确保UTF-8编码支持中文
            env = os.environ.copy()
            env['LANG'] = 'zh_CN.UTF-8'
            env['LC_ALL'] = 'zh_CN.UTF-8'
            env['TERM'] = 'xterm-256color'

            # 如果系统没有中文locale，回退到英文UTF-8
            try:
                import locale
                locale.setlocale(locale.LC_ALL, 'zh_CN.UTF-8')
            except:
                env['LANG'] = 'en_US.UTF-8'
                env['LC_ALL'] = 'en_US.UTF-8'
                print("[终端] 警告：系统不支持中文locale，使用英文UTF-8")

            # 启动shell进程
            self.process = subprocess.Popen(
                ['/bin/bash', '--login'],  # 使用登录shell，加载完整环境
                stdin=self.slave_fd,
                stdout=self.slave_fd,
                stderr=self.slave_fd,
                env=env,  # 传递环境变量
                preexec_fn=os.setsid
            )

            self.running = True

            # 启动输出读取线程
            self.output_thread = threading.Thread(target=self.read_output)
            self.output_thread.daemon = True
            self.output_thread.start()

            print("[终端] 终端会话已启动（UTF-8编码）")

        except Exception as e:
            print(f"[错误] 启动终端失败: {e}")
            self.running = False

    def handle_input(self, command):
        """处理终端输入"""
        if not self.running or self.master_fd is None:
            return

        try:
            if isinstance(command, str):
                command = command.encode('utf-8')
            os.write(self.master_fd, command)
        except Exception as e:
            print(f"[错误] 写入终端失败: {e}")

    def read_output(self):
        """读取终端输出"""
        while self.running:
            try:
                # 使用select检查是否有数据可读
                r, _, _ = select.select([self.master_fd], [], [], 0.1)

                if r:
                    try:
                        output = os.read(self.master_fd, 8192)
                        if output:
                            # 发送输出到客户端
                            msg = Protocol.pack_message(
                                Protocol.MSG_TERMINAL_OUTPUT,
                                output
                            )
                            self.client_socket.send(msg)
                    except OSError:
                        # 终端已关闭
                        break

            except Exception as e:
                print(f"[错误] 读取终端输出失败: {e}")
                break

        print("[终端] 输出读取线程已停止")

    def stop(self):
        """停止终端"""
        self.running = False

        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=2)
            except:
                try:
                    self.process.kill()
                except:
                    pass

        if self.master_fd:
            try:
                os.close(self.master_fd)
            except:
                pass

        if self.slave_fd:
            try:
                os.close(self.slave_fd)
            except:
                pass

        print("[终端] 终端会话已停止")
