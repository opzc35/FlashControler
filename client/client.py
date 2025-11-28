"""
FlashControler Windows客户端主程序
提供GUI界面进行远程终端和文件传输
"""
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import threading
import sys
import os
import re

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from client.connection import ClientConnection
from client.update_manager import UpdateManager
from common.config import Config


class RemoteDirDialog:
    """远程目录选择对话框"""

    def __init__(self, parent, connection):
        self.connection = connection
        self.result = None
        self.current_path = "/"
        self.loading = False

        # 创建对话框窗口
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("选择远程目录")
        self.dialog.geometry("500x600")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        self.setup_ui()
        self.load_directory("/")

        # 等待对话框关闭
        self.dialog.wait_window()

    def setup_ui(self):
        """设置UI"""
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 当前路径显示
        path_frame = ttk.Frame(main_frame)
        path_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(path_frame, text="当前路径:").pack(side=tk.LEFT)
        self.path_label = ttk.Label(path_frame, text="/", font=("", 10, "bold"))
        self.path_label.pack(side=tk.LEFT, padx=(5, 0))

        # 加载状态标签
        self.status_label = ttk.Label(path_frame, text="", foreground="gray")
        self.status_label.pack(side=tk.RIGHT)

        # 目录列表
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)

        # 添加滚动条
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.dir_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set)
        self.dir_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.dir_listbox.yview)

        # 双击加载子目录
        self.dir_listbox.bind('<Double-Button-1>', self.on_double_click)

        # 按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(button_frame, text="🔄 刷新", command=self.refresh_current).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="✓ 选择此目录", command=self.select_current).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="取消", command=self.dialog.destroy).pack(side=tk.LEFT)

    def load_directory(self, path):
        """加载目录内容（异步）"""
        if self.loading:
            return  # 如果正在加载，忽略新请求

        self.loading = True
        self.current_path = path
        self.path_label.config(text=path)
        self.dir_listbox.delete(0, tk.END)
        self.status_label.config(text="正在加载...")
        self.dir_listbox.config(state=tk.DISABLED)

        # 在后台线程中加载
        def load_in_background():
            result, error = self.connection.list_dir(path)
            # 使用 after 在主线程中更新 GUI
            self.dialog.after(0, self.on_dir_loaded, path, result, error)

        thread = threading.Thread(target=load_in_background, daemon=True)
        thread.start()

    def on_dir_loaded(self, path, result, error):
        """目录加载完成回调（在主线程中调用）"""
        self.loading = False
        self.status_label.config(text="")
        self.dir_listbox.config(state=tk.NORMAL)

        if error:
            messagebox.showerror("错误", f"无法加载目录: {error}", parent=self.dialog)
            return

        # 添加上级目录项（如果不是根目录）
        if path != "/":
            self.dir_listbox.insert(tk.END, ".. (上级目录)")

        items = result.get('items', [])
        if not items:
            self.dir_listbox.insert(tk.END, "(空目录)")
        else:
            for item in items:
                self.dir_listbox.insert(tk.END, f"📁 {item['name']}")

    def on_double_click(self, event):
        """双击项目时加载该目录"""
        selection = self.dir_listbox.curselection()
        if not selection:
            return

        index = selection[0]
        item_text = self.dir_listbox.get(index)

        if item_text == "(空目录)":
            return

        if item_text == ".. (上级目录)":
            # 加载上级目录
            parent_path = os.path.dirname(self.current_path)
            if parent_path == "":
                parent_path = "/"
            self.load_directory(parent_path)
        else:
            # 移除前面的emoji符号，获取目录名
            dir_name = item_text.replace("📁 ", "")
            new_path = os.path.join(self.current_path, dir_name)
            self.load_directory(new_path)

    def refresh_current(self):
        """刷新当前目录"""
        self.load_directory(self.current_path)

    def select_current(self):
        """选择当前目录"""
        self.result = self.current_path
        self.dialog.destroy()


class FlashClientGUI:
    """FlashControler客户端GUI"""

    # ANSI转义序列正则表达式（用于过滤终端控制码）
    ANSI_ESCAPE_PATTERN = re.compile(r'\x1b\[[0-9;]*[a-zA-Z]|\x1b\][0-9;]*;[^\x07]*\x07|\x1b\][^\x07]*\x07|\x1b\[\?[0-9;]*[a-zA-Z]|\x1b[=>]|\r')

    def __init__(self, root):
        self.root = root
        self.root.title("FlashControler - Windows客户端")
        self.root.geometry("900x700")

        self.config = Config("config/settings.json")
        self.connection = ClientConnection()
        self.update_manager = UpdateManager(
            current_version=self.config.get('update', 'current_version', '1.0.0'),
            update_url=self.config.get('update', 'update_url', '')
        )

        # 命令历史
        self.command_history = []  # 命令历史列表
        self.history_index = -1  # 当前历史索引
        self.current_input = ""  # 临时保存当前输入
        self.max_history = 100  # 最大历史记录数

        self.setup_ui()
        self.setup_callbacks()

        # 启动时检查更新
        if self.config.get('update', 'check_on_startup', True):
            self.check_update()

    def setup_ui(self):
        """设置UI"""
        # 创建主容器
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)

        # 连接区域
        self.setup_connection_frame(main_frame)

        # 创建标签页
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))

        # 终端标签页
        self.setup_terminal_tab()

        # 文件传输标签页
        self.setup_file_transfer_tab()

        # 关于标签页
        self.setup_about_tab()

    def setup_connection_frame(self, parent):
        """设置连接区域"""
        conn_frame = ttk.LabelFrame(parent, text="连接设置", padding="10")
        conn_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))

        # 服务器地址
        ttk.Label(conn_frame, text="服务器地址:").grid(row=0, column=0, sticky=tk.W)
        self.host_entry = ttk.Entry(conn_frame, width=20)
        self.host_entry.grid(row=0, column=1, padx=5)
        self.host_entry.insert(0, self.config.get('client', 'last_host', '192.168.1.100'))

        # 端口
        ttk.Label(conn_frame, text="端口:").grid(row=0, column=2, padx=(10, 0))
        self.port_entry = ttk.Entry(conn_frame, width=10)
        self.port_entry.grid(row=0, column=3, padx=5)
        self.port_entry.insert(0, str(self.config.get('client', 'last_port', 9999)))

        # 密码
        ttk.Label(conn_frame, text="密码:").grid(row=0, column=4, padx=(10, 0))
        self.password_entry = ttk.Entry(conn_frame, width=15, show="*")
        self.password_entry.grid(row=0, column=5, padx=5)
        self.password_entry.insert(0, "flashcontrol123")

        # 连接按钮
        self.connect_btn = ttk.Button(conn_frame, text="连接", command=self.toggle_connection)
        self.connect_btn.grid(row=0, column=6, padx=(10, 0))

        # 状态标签
        self.status_label = ttk.Label(conn_frame, text="未连接", foreground="red")
        self.status_label.grid(row=0, column=7, padx=(10, 0))

    def setup_terminal_tab(self):
        """设置终端标签页"""
        terminal_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(terminal_frame, text="远程终端")

        # 终端输出区域
        self.terminal_output = scrolledtext.ScrolledText(
            terminal_frame,
            height=25,
            width=100,
            bg="black",
            fg="white",
            font=("Consolas", 10)
        )
        self.terminal_output.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 终端输入区域
        input_frame = ttk.Frame(terminal_frame)
        input_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 0))

        ttk.Label(input_frame, text="命令:").grid(row=0, column=0)
        self.terminal_input = ttk.Entry(input_frame)
        self.terminal_input.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        self.terminal_input.bind('<Return>', self.send_terminal_command)
        self.terminal_input.bind('<Up>', self.navigate_history_up)
        self.terminal_input.bind('<Down>', self.navigate_history_down)
        self.terminal_input.bind('<Control-h>', self.show_command_history)

        self.send_btn = ttk.Button(input_frame, text="发送", command=self.send_terminal_command)
        self.send_btn.grid(row=0, column=2)

        # 历史按钮
        self.history_btn = ttk.Button(input_frame, text="📜 历史", command=self.show_command_history)
        self.history_btn.grid(row=0, column=3, padx=(5, 0))

        self.clear_btn = ttk.Button(input_frame, text="清屏", command=self.clear_terminal)
        self.clear_btn.grid(row=0, column=4, padx=(5, 0))

        input_frame.columnconfigure(1, weight=1)
        terminal_frame.columnconfigure(0, weight=1)
        terminal_frame.rowconfigure(0, weight=1)

    def setup_file_transfer_tab(self):
        """设置文件传输标签页"""
        file_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(file_frame, text="文件传输")

        # 文件选择
        ttk.Label(file_frame, text="选择文件:").grid(row=0, column=0, sticky=tk.W)
        self.file_path_var = tk.StringVar()
        self.file_path_entry = ttk.Entry(file_frame, textvariable=self.file_path_var, width=50)
        self.file_path_entry.grid(row=0, column=1, padx=5, sticky=(tk.W, tk.E))

        self.browse_btn = ttk.Button(file_frame, text="浏览", command=self.browse_file)
        self.browse_btn.grid(row=0, column=2)

        # 目标路径
        ttk.Label(file_frame, text="目标路径:").grid(row=1, column=0, sticky=tk.W, pady=(10, 0))
        self.target_path_var = tk.StringVar(value="/tmp")
        self.target_path_entry = ttk.Entry(file_frame, textvariable=self.target_path_var, width=50)
        self.target_path_entry.grid(row=1, column=1, padx=5, pady=(10, 0), sticky=(tk.W, tk.E))

        self.browse_remote_btn = ttk.Button(file_frame, text="浏览远程", command=self.browse_remote_dir)
        self.browse_remote_btn.grid(row=1, column=2, pady=(10, 0))

        # 上传按钮
        self.upload_btn = ttk.Button(file_frame, text="上传文件", command=self.upload_file)
        self.upload_btn.grid(row=2, column=0, columnspan=3, pady=(20, 0))

        # 进度条
        ttk.Label(file_frame, text="传输进度:").grid(row=3, column=0, sticky=tk.W, pady=(20, 0))
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            file_frame,
            variable=self.progress_var,
            maximum=100,
            length=400
        )
        self.progress_bar.grid(row=3, column=1, columnspan=2, pady=(20, 0), sticky=(tk.W, tk.E))

        # 进度标签
        self.progress_label = ttk.Label(file_frame, text="")
        self.progress_label.grid(row=4, column=0, columnspan=3, pady=(5, 0))

        # 传输日志
        ttk.Label(file_frame, text="传输日志:").grid(row=5, column=0, sticky=tk.W, pady=(20, 0))
        self.transfer_log = scrolledtext.ScrolledText(file_frame, height=15, width=80)
        self.transfer_log.grid(row=6, column=0, columnspan=3, pady=(5, 0), sticky=(tk.W, tk.E, tk.N, tk.S))

        file_frame.columnconfigure(1, weight=1)
        file_frame.rowconfigure(6, weight=1)

    def setup_about_tab(self):
        """设置关于标签页"""
        about_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(about_frame, text="关于")

        # 标题
        title_label = ttk.Label(
            about_frame,
            text="FlashControler",
            font=("Arial", 20, "bold")
        )
        title_label.grid(row=0, column=0, pady=(0, 10))

        # 版本信息
        version = self.config.get('update', 'current_version', '1.0.0')
        version_label = ttk.Label(about_frame, text=f"版本: {version}")
        version_label.grid(row=1, column=0, pady=5)

        # 描述
        desc_label = ttk.Label(
            about_frame,
            text="Windows到Linux的远程控制工具\n支持远程终端和文件传输",
            justify=tk.CENTER
        )
        desc_label.grid(row=2, column=0, pady=20)

        # 检查更新按钮
        self.update_btn = ttk.Button(about_frame, text="检查更新", command=self.check_update)
        self.update_btn.grid(row=3, column=0, pady=10)

    def setup_callbacks(self):
        """设置回调函数"""
        self.connection.register_callback('terminal_output', self.on_terminal_output)
        self.connection.register_callback('disconnected', self.on_disconnected)
        self.connection.register_callback('file_progress', self.on_file_progress)
        self.connection.register_callback('update_info', self.on_update_info)
        self.connection.register_callback('error', self.on_error)

    def toggle_connection(self):
        """切换连接状态"""
        if not self.connection.connected:
            # 连接
            host = self.host_entry.get().strip()
            port = int(self.port_entry.get().strip())
            password = self.password_entry.get()

            if not host or not port:
                messagebox.showerror("错误", "请输入服务器地址和端口")
                return

            self.status_label.config(text="连接中...", foreground="orange")
            self.connect_btn.config(state="disabled")

            # 在后台线程中连接
            threading.Thread(target=self._connect_thread, args=(host, port, password)).start()
        else:
            # 断开连接
            self.connection.disconnect()
            self.on_disconnected()

    def _connect_thread(self, host, port, password):
        """连接线程"""
        success, message = self.connection.connect(host, port, password)

        # 更新UI（需要在主线程中执行）
        self.root.after(0, self._on_connect_result, success, message, host, port)

    def _on_connect_result(self, success, message, host, port):
        """连接结果处理"""
        self.connect_btn.config(state="normal")

        if success:
            self.status_label.config(text="已连接", foreground="green")
            self.connect_btn.config(text="断开")

            # 保存连接信息
            self.config.set('client', 'last_host', host)
            self.config.set('client', 'last_port', port)

            self.append_terminal_output(f"\n=== 已连接到 {host}:{port} ===\n")
        else:
            self.status_label.config(text="未连接", foreground="red")
            messagebox.showerror("连接失败", message)

    def on_disconnected(self):
        """断开连接回调"""
        self.root.after(0, self._update_disconnect_ui)

    def _update_disconnect_ui(self):
        """更新断开连接的UI"""
        self.status_label.config(text="未连接", foreground="red")
        self.connect_btn.config(text="连接")
        self.append_terminal_output("\n=== 连接已断开 ===\n")

    def send_terminal_command(self, event=None):
        """发送终端命令"""
        if not self.connection.connected:
            messagebox.showwarning("警告", "请先连接到服务器")
            return

        command = self.terminal_input.get()
        if command:
            # 添加到命令历史
            self.add_to_history(command)

            # 添加换行符
            if not command.endswith('\n'):
                command += '\n'

            self.connection.send_terminal_input(command)
            self.terminal_input.delete(0, tk.END)

    def on_terminal_output(self, output):
        """终端输出回调"""
        if isinstance(output, bytes):
            try:
                # 优先尝试UTF-8解码
                output = output.decode('utf-8')
            except UnicodeDecodeError:
                try:
                    # 如果UTF-8失败，尝试GBK（中文Windows环境）
                    output = output.decode('gbk')
                except UnicodeDecodeError:
                    # 最后使用替换模式，避免程序崩溃
                    output = output.decode('utf-8', errors='replace')
                    print("[警告] 终端输出包含无法识别的字符")

        # 过滤ANSI转义序列（终端控制码）
        output = self.strip_ansi_codes(output)

        self.root.after(0, self.append_terminal_output, output)

    @staticmethod
    def strip_ansi_codes(text):
        """移除ANSI转义序列

        移除常见的ANSI控制码，包括：
        - 颜色控制码
        - 光标移动
        - 屏幕清除
        - bracketed paste mode ([?2004h/l)
        - 其他终端控制序列
        """
        return FlashClientGUI.ANSI_ESCAPE_PATTERN.sub('', text)

    def add_to_history(self, command):
        """添加命令到历史"""
        command = command.strip()
        if not command:
            return

        # 避免重复连续命令
        if self.command_history and self.command_history[-1] == command:
            return

        # 如果命令已存在，先移除旧的
        if command in self.command_history:
            self.command_history.remove(command)

        # 添加到历史末尾
        self.command_history.append(command)

        # 限制历史记录数量
        if len(self.command_history) > self.max_history:
            self.command_history.pop(0)

        # 重置索引
        self.history_index = -1

    def navigate_history_up(self, event):
        """向前浏览历史（上箭头）"""
        if not self.command_history:
            return "break"

        # 第一次按上箭头，保存当前输入
        if self.history_index == -1:
            self.current_input = self.terminal_input.get()
            self.history_index = len(self.command_history) - 1
        elif self.history_index > 0:
            self.history_index -= 1

        # 显示历史命令
        self.terminal_input.delete(0, tk.END)
        self.terminal_input.insert(0, self.command_history[self.history_index])
        return "break"

    def navigate_history_down(self, event):
        """向后浏览历史（下箭头）"""
        if self.history_index == -1:
            return "break"

        if self.history_index < len(self.command_history) - 1:
            self.history_index += 1
            self.terminal_input.delete(0, tk.END)
            self.terminal_input.insert(0, self.command_history[self.history_index])
        else:
            # 到达末尾，恢复当前输入
            self.history_index = -1
            self.terminal_input.delete(0, tk.END)
            self.terminal_input.insert(0, self.current_input)

        return "break"

    def show_command_history(self, event=None):
        """显示命令历史选择窗口"""
        if not self.command_history:
            messagebox.showinfo("命令历史", "还没有历史命令记录")
            return "break" if event else None

        # 创建历史选择窗口
        history_window = tk.Toplevel(self.root)
        history_window.title("命令历史")
        history_window.geometry("600x400")
        history_window.transient(self.root)
        history_window.grab_set()

        # 说明标签
        info_label = ttk.Label(
            history_window,
            text="双击命令或选择后点击\"使用\"按钮",
            foreground="#7f8c8d"
        )
        info_label.pack(pady=10)

        # 创建列表框架
        list_frame = ttk.Frame(history_window)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # 滚动条
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 列表框
        listbox = tk.Listbox(
            list_frame,
            font=("Consolas", 10),
            yscrollcommand=scrollbar.set,
            selectmode=tk.SINGLE,
            activestyle='dotbox'
        )
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=listbox.yview)

        # 添加历史命令（从新到旧）
        for cmd in reversed(self.command_history):
            listbox.insert(tk.END, cmd)

        def use_selected():
            """使用选中的命令"""
            selection = listbox.curselection()
            if selection:
                command = listbox.get(selection[0])
                self.terminal_input.delete(0, tk.END)
                self.terminal_input.insert(0, command)
                history_window.destroy()
                self.terminal_input.focus()
            else:
                messagebox.showwarning("未选择", "请先选择一条命令")

        def on_double_click(event):
            """双击时使用命令"""
            use_selected()

        # 双击选择
        listbox.bind('<Double-Button-1>', on_double_click)

        # 按钮区域
        button_frame = ttk.Frame(history_window)
        button_frame.pack(pady=10)

        use_btn = ttk.Button(button_frame, text="使用选中的命令", command=use_selected)
        use_btn.pack(side=tk.LEFT, padx=5)

        cancel_btn = ttk.Button(button_frame, text="取消", command=history_window.destroy)
        cancel_btn.pack(side=tk.LEFT, padx=5)

        # 选中第一项
        if listbox.size() > 0:
            listbox.selection_set(0)
            listbox.focus()

        return "break" if event else None

    def append_terminal_output(self, text):
        """追加终端输出"""
        self.terminal_output.insert(tk.END, text)
        self.terminal_output.see(tk.END)

    def clear_terminal(self):
        """清空终端"""
        self.terminal_output.delete(1.0, tk.END)

    def browse_file(self):
        """浏览文件"""
        filename = filedialog.askopenfilename(
            title="选择要上传的文件",
            filetypes=[("所有文件", "*.*")]
        )
        if filename:
            self.file_path_var.set(filename)

    def browse_remote_dir(self):
        """浏览远程目录"""
        if not self.connection.connected:
            messagebox.showwarning("警告", "请先连接到服务器")
            return

        dialog = RemoteDirDialog(self.root, self.connection)
        if dialog.result:
            self.target_path_var.set(dialog.result)

    def upload_file(self):
        """上传文件"""
        if not self.connection.connected:
            messagebox.showwarning("警告", "请先连接到服务器")
            return

        file_path = self.file_path_var.get()
        target_path = self.target_path_var.get()

        if not file_path or not os.path.exists(file_path):
            messagebox.showerror("错误", "请选择有效的文件")
            return

        if not target_path:
            messagebox.showerror("错误", "请输入目标路径")
            return

        self.upload_btn.config(state="disabled")
        self.progress_var.set(0)
        self.progress_label.config(text="")

        # 在后台线程中上传
        threading.Thread(target=self._upload_thread, args=(file_path, target_path)).start()

    def _upload_thread(self, file_path, target_path):
        """上传线程"""
        self.log_transfer(f"开始上传: {os.path.basename(file_path)}")

        success, message = self.connection.upload_file(file_path, target_path)

        # 更新UI
        self.root.after(0, self._on_upload_complete, success, message)

    def _on_upload_complete(self, success, message):
        """上传完成"""
        self.upload_btn.config(state="normal")

        if success:
            self.log_transfer(f"上传成功: {message}")
            messagebox.showinfo("成功", message)
        else:
            self.log_transfer(f"上传失败: {message}")
            messagebox.showerror("失败", message)

    def on_file_progress(self, progress, sent, total):
        """文件传输进度回调"""
        self.root.after(0, self._update_progress, progress, sent, total)

    def _update_progress(self, progress, sent, total):
        """更新进度"""
        self.progress_var.set(progress)
        self.progress_label.config(text=f"{progress:.1f}% ({sent}/{total} 字节)")

    def log_transfer(self, message):
        """记录传输日志"""
        self.root.after(0, self._append_log, message)

    def _append_log(self, message):
        """追加日志"""
        self.transfer_log.insert(tk.END, f"{message}\n")
        self.transfer_log.see(tk.END)

    def check_update(self):
        """检查更新"""
        self.update_btn.config(state="disabled", text="检查中...")

        threading.Thread(target=self._check_update_thread).start()

    def _check_update_thread(self):
        """检查更新线程"""
        update_info = self.update_manager.check_update()

        self.root.after(0, self._on_update_checked, update_info)

    def _on_update_checked(self, update_info):
        """更新检查完成"""
        self.update_btn.config(state="normal", text="检查更新")

        if update_info is None:
            messagebox.showerror("错误", "检查更新失败，请检查网络连接")
        elif update_info.get('has_update'):
            result = messagebox.askyesno(
                "发现新版本",
                f"发现新版本 {update_info['latest_version']}\n"
                f"当前版本 {update_info['current_version']}\n\n"
                f"是否前往下载？"
            )
            if result:
                import webbrowser
                webbrowser.open(update_info['download_url'])
        else:
            messagebox.showinfo("检查更新", "当前已是最新版本")

    def on_update_info(self, info):
        """更新信息回调"""
        pass

    def on_error(self, error):
        """错误回调"""
        self.root.after(0, messagebox.showerror, "错误", str(error))


def main():
    """主函数"""
    root = tk.Tk()
    app = FlashClientGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
