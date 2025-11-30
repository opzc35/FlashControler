"""
FlashControler Windows客户端主程序 (PyQt5版本)
提供现代化、美观的GUI界面进行远程终端和文件传输
"""
import sys
import os
import re
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QTabWidget, QLabel, QLineEdit,
                             QPushButton, QTextEdit, QFileDialog, QProgressBar,
                             QMessageBox, QGroupBox, QGridLayout, QSplitter,
                             QDialog, QListWidget, QListWidgetItem, QTreeWidget,
                             QTreeWidgetItem)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QIcon, QPalette, QColor, QTextCursor, QKeySequence

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from client.connection import ClientConnection
from client.update_manager import UpdateManager
from common.config import Config
from common.version import __version__


class HistoryDialog(QDialog):
    """命令历史选择对话框"""

    def __init__(self, history_list, parent=None):
        super().__init__(parent)
        self.selected_command = None
        self.history_list = history_list

        self.setWindowTitle("命令历史")
        self.setModal(True)
        self.resize(600, 400)

        self.setup_ui()

    def setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)

        # 说明标签
        info_label = QLabel("双击命令或选择后点击\"使用\"按钮")
        info_label.setStyleSheet("color: #7f8c8d; margin-bottom: 10px;")
        layout.addWidget(info_label)

        # 历史命令列表
        self.list_widget = QListWidget()
        self.list_widget.setAlternatingRowColors(True)
        self.list_widget.setStyleSheet("""
            QListWidget {
                border: 2px solid #dcdde1;
                border-radius: 5px;
                background-color: white;
                font-size: 11px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #ecf0f1;
            }
            QListWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #ecf0f1;
            }
        """)

        # 添加历史命令（从新到旧显示）
        for cmd in reversed(self.history_list):
            item = QListWidgetItem(cmd)
            item.setFont(QFont("Consolas", 10))
            self.list_widget.addItem(item)

        # 双击选择
        self.list_widget.itemDoubleClicked.connect(self.on_item_double_clicked)
        layout.addWidget(self.list_widget)

        # 按钮区域
        button_layout = QHBoxLayout()

        # 使用按钮
        use_btn = QPushButton("使用选中的命令")
        use_btn.setMinimumHeight(35)
        use_btn.clicked.connect(self.use_selected)
        button_layout.addWidget(use_btn)

        # 取消按钮
        cancel_btn = QPushButton("取消")
        cancel_btn.setMinimumHeight(35)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)

        # 应用样式
        self.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)

    def on_item_double_clicked(self, item):
        """双击项目时选择"""
        self.selected_command = item.text()
        self.accept()

    def use_selected(self):
        """使用选中的命令"""
        current_item = self.list_widget.currentItem()
        if current_item:
            self.selected_command = current_item.text()
            self.accept()
        else:
            QMessageBox.warning(self, "未选择", "请先选择一条命令")


class DirLoadThread(QThread):
    """目录加载线程"""
    finished = pyqtSignal(str, object, object)  # path, result, error

    def __init__(self, connection, path):
        super().__init__()
        self.connection = connection
        self.path = path

    def run(self):
        """在后台线程中加载目录"""
        result, error = self.connection.list_dir(self.path)
        self.finished.emit(self.path, result, error)


class RemoteDirDialog(QDialog):
    """远程目录选择对话框"""

    # 定义信号
    dir_loaded = pyqtSignal(str, object, object)  # path, result, error

    def __init__(self, connection, parent=None):
        super().__init__(parent)
        self.connection = connection
        self.selected_path = None
        self.loading = False

        self.setWindowTitle("选择远程目录")
        self.setModal(True)
        self.resize(500, 600)

        self.setup_ui()

        # 连接信号
        self.dir_loaded.connect(self.on_dir_loaded)

        # 加载根目录
        self.load_directory("/")

    def setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)

        # 当前路径显示
        path_layout = QHBoxLayout()
        path_layout.addWidget(QLabel("当前路径:"))
        self.current_path_label = QLabel("/")
        self.current_path_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        path_layout.addWidget(self.current_path_label)
        path_layout.addStretch()

        # 加载状态标签
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #7f8c8d; font-style: italic;")
        path_layout.addWidget(self.status_label)

        layout.addLayout(path_layout)

        # 目录树
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["目录名"])
        self.tree.itemDoubleClicked.connect(self.on_item_double_clicked)
        self.tree.setStyleSheet("""
            QTreeWidget {
                border: 2px solid #dcdde1;
                border-radius: 5px;
                background-color: white;
                font-size: 11px;
            }
            QTreeWidget::item {
                padding: 5px;
            }
            QTreeWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
        """)
        layout.addWidget(self.tree)

        # 按钮区域
        button_layout = QHBoxLayout()

        # 刷新按钮
        refresh_btn = QPushButton("🔄 刷新")
        refresh_btn.clicked.connect(self.refresh_current)
        button_layout.addWidget(refresh_btn)

        # 选择按钮
        select_btn = QPushButton("✓ 选择此目录")
        select_btn.clicked.connect(self.select_current)
        button_layout.addWidget(select_btn)

        # 取消按钮
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)

        # 应用样式
        self.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
                min-height: 30px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)

    def load_directory(self, path):
        """加载目录内容（异步）"""
        if self.loading:
            return  # 如果正在加载，忽略新请求

        self.loading = True
        self.tree.clear()
        self.current_path_label.setText(path)
        self.status_label.setText("正在加载...")

        # 禁用按钮
        self.tree.setEnabled(False)

        # 创建并启动加载线程
        self.load_thread = DirLoadThread(self.connection, path)
        self.load_thread.finished.connect(self.on_dir_loaded)
        self.load_thread.start()

    def on_dir_loaded(self, path, result, error):
        """目录加载完成回调"""
        self.loading = False
        self.status_label.setText("")
        self.tree.setEnabled(True)

        if error:
            QMessageBox.warning(self, "错误", f"无法加载目录: {error}")
            return

        # 添加上级目录项（如果不是根目录）
        if path != "/":
            parent_item = QTreeWidgetItem(self.tree, [".. (上级目录)"])
            parent_item.setData(0, Qt.UserRole, os.path.dirname(path))

        items = result.get('items', [])
        if not items:
            # 显示空目录提示
            empty_item = QTreeWidgetItem(self.tree, ["(空目录)"])
            empty_item.setDisabled(True)
        else:
            for item in items:
                tree_item = QTreeWidgetItem(self.tree, [f"📁 {item['name']}"])
                tree_item.setData(0, Qt.UserRole, item['path'])

    def on_item_double_clicked(self, item, column):
        """双击项目时加载该目录"""
        path = item.data(0, Qt.UserRole)
        if path:
            self.load_directory(path)

    def refresh_current(self):
        """刷新当前目录"""
        current_path = self.current_path_label.text()
        self.load_directory(current_path)

    def select_current(self):
        """选择当前目录"""
        self.selected_path = self.current_path_label.text()
        self.accept()

    def get_selected_path(self):
        """获取选中的路径"""
        return self.selected_path


class CommandLineEdit(QLineEdit):
    """带命令历史功能的输入框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.command_history = []  # 命令历史列表
        self.history_index = -1  # 当前历史索引（-1表示不在历史中）
        self.current_input = ""  # 临时保存当前输入
        self.max_history = 100  # 最大历史记录数
        self.parent_window = parent  # 保存父窗口引用

    def show_history_dialog(self):
        """显示历史选择对话框"""
        if not self.command_history:
            QMessageBox.information(
                self.parent_window,
                "命令历史",
                "还没有历史命令记录"
            )
            return

        dialog = HistoryDialog(self.command_history, self.parent_window)
        if dialog.exec_() == QDialog.Accepted and dialog.selected_command:
            self.setText(dialog.selected_command)
            self.setFocus()

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

    def keyPressEvent(self, event):
        """处理按键事件"""
        # Ctrl+H: 显示历史对话框
        if event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_H:
            self.show_history_dialog()
            return

        if event.key() == Qt.Key_Up:
            # 上箭头：向前浏览历史（从新到旧）
            self.navigate_history_up()
        elif event.key() == Qt.Key_Down:
            # 下箭头：向后浏览历史（从旧到新）
            self.navigate_history_down()
        else:
            # 其他键：重置历史浏览
            if self.history_index == -1:
                super().keyPressEvent(event)
            else:
                # 如果在浏览历史时输入，退出历史模式
                self.history_index = -1
                super().keyPressEvent(event)

    def navigate_history_up(self):
        """向前浏览历史"""
        if not self.command_history:
            return

        # 第一次按上箭头，保存当前输入
        if self.history_index == -1:
            self.current_input = self.text()
            self.history_index = len(self.command_history) - 1
        elif self.history_index > 0:
            self.history_index -= 1

        # 显示历史命令
        self.setText(self.command_history[self.history_index])

    def navigate_history_down(self):
        """向后浏览历史"""
        if self.history_index == -1:
            return

        if self.history_index < len(self.command_history) - 1:
            self.history_index += 1
            self.setText(self.command_history[self.history_index])
        else:
            # 到达末尾，恢复当前输入
            self.history_index = -1
            self.setText(self.current_input)


class ConnectionThread(QThread):
    """连接线程"""
    result = pyqtSignal(bool, str)

    def __init__(self, connection, host, port, password):
        super().__init__()
        self.connection = connection
        self.host = host
        self.port = port
        self.password = password

    def run(self):
        success, message = self.connection.connect(self.host, self.port, self.password)
        self.result.emit(success, message)


class UploadThread(QThread):
    """上传线程"""
    result = pyqtSignal(bool, str)

    def __init__(self, connection, file_path, target_path):
        super().__init__()
        self.connection = connection
        self.file_path = file_path
        self.target_path = target_path

    def run(self):
        success, message = self.connection.upload_file(self.file_path, self.target_path)
        self.result.emit(success, message)


class UpdateCheckThread(QThread):
    """更新检查线程"""
    result = pyqtSignal(object)

    def __init__(self, update_manager):
        super().__init__()
        self.update_manager = update_manager

    def run(self):
        update_info = self.update_manager.check_update()
        self.result.emit(update_info)


class FlashClientGUI(QMainWindow):
    """FlashControler客户端GUI (PyQt5版本)"""

    # ANSI转义序列正则表达式（用于过滤终端控制码）
    ANSI_ESCAPE_PATTERN = re.compile(r'\x1b\[[0-9;]*[a-zA-Z]|\x1b\][0-9;]*;[^\x07]*\x07|\x1b\][^\x07]*\x07|\x1b\[\?[0-9;]*[a-zA-Z]|\x1b[=>]|\r')

    # 定义信号（用于线程安全的GUI更新）
    terminal_output_signal = pyqtSignal(str)
    disconnected_signal = pyqtSignal()
    file_progress_signal = pyqtSignal(float, int, int)

    def __init__(self):
        super().__init__()

        self.config = Config("config/settings.json")
        self.connection = ClientConnection()
        self.update_manager = UpdateManager(
            current_version=__version__,
            update_url=self.config.get('update', 'update_url', '')
        )

        self.setup_ui()
        self.setup_callbacks()
        self.setup_signals()  # 连接信号到槽
        self.apply_styles()

        # 启动时检查更新
        if self.config.get('update', 'check_on_startup', True):
            QTimer.singleShot(1000, self.check_update)

    def setup_ui(self):
        """设置UI"""
        self.setWindowTitle("FlashControler - 远程控制客户端")
        self.setGeometry(100, 100, 1200, 800)

        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # 连接区域
        self.setup_connection_section(main_layout)

        # 标签页
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        main_layout.addWidget(self.tabs)

        # 创建各个标签页
        self.setup_terminal_tab()
        self.setup_file_transfer_tab()
        self.setup_about_tab()

    def setup_connection_section(self, parent_layout):
        """设置连接区域"""
        conn_group = QGroupBox("连接设置")
        conn_layout = QGridLayout()
        conn_group.setLayout(conn_layout)

        # 服务器地址
        conn_layout.addWidget(QLabel("服务器地址:"), 0, 0)
        self.host_input = QLineEdit()
        self.host_input.setPlaceholderText("例如: 192.168.1.100")
        self.host_input.setText(self.config.get('client', 'last_host', ''))
        conn_layout.addWidget(self.host_input, 0, 1)

        # 端口
        conn_layout.addWidget(QLabel("端口:"), 0, 2)
        self.port_input = QLineEdit()
        self.port_input.setPlaceholderText("9999")
        self.port_input.setText(str(self.config.get('client', 'last_port', 9999)))
        self.port_input.setMaximumWidth(100)
        conn_layout.addWidget(self.port_input, 0, 3)

        # 密码
        conn_layout.addWidget(QLabel("密码:"), 0, 4)
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setText("flashcontrol123")
        conn_layout.addWidget(self.password_input, 0, 5)

        # 连接按钮
        self.connect_btn = QPushButton("连接")
        self.connect_btn.setMinimumWidth(120)
        self.connect_btn.clicked.connect(self.toggle_connection)
        conn_layout.addWidget(self.connect_btn, 0, 6)

        # 状态指示器
        status_container = QWidget()
        status_layout = QHBoxLayout(status_container)
        status_layout.setContentsMargins(0, 0, 0, 0)

        self.status_indicator = QLabel("●")
        self.status_indicator.setStyleSheet("color: #e74c3c; font-size: 16px;")
        self.status_label = QLabel("未连接")
        self.status_label.setStyleSheet("color: #e74c3c; font-weight: bold;")

        status_layout.addWidget(self.status_indicator)
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()

        conn_layout.addWidget(status_container, 0, 7)

        parent_layout.addWidget(conn_group)

    def setup_terminal_tab(self):
        """设置终端标签页"""
        terminal_widget = QWidget()
        terminal_layout = QVBoxLayout(terminal_widget)
        terminal_layout.setSpacing(10)

        # 终端输出区域
        self.terminal_output = QTextEdit()
        self.terminal_output.setReadOnly(True)

        # 使用支持中文的等宽字体
        # 优先使用中文等宽字体，回退到Consolas
        terminal_font = QFont()
        terminal_font.setStyleHint(QFont.Monospace)
        terminal_font.setFamily("Microsoft YaHei Mono, Consolas, Monaco, Courier New")
        terminal_font.setPointSize(10)
        self.terminal_output.setFont(terminal_font)

        self.terminal_output.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: 2px solid #3c3c3c;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        terminal_layout.addWidget(self.terminal_output)

        # 命令输入区域
        input_container = QWidget()
        input_layout = QHBoxLayout(input_container)
        input_layout.setContentsMargins(0, 0, 0, 0)

        input_layout.addWidget(QLabel("命令:"))

        self.terminal_input = CommandLineEdit(self)
        self.terminal_input.setPlaceholderText("输入命令，按Enter发送（↑↓键切换历史，Ctrl+H打开历史列表）...")
        self.terminal_input.returnPressed.connect(self.send_terminal_command)
        input_layout.addWidget(self.terminal_input)

        self.send_btn = QPushButton("发送")
        self.send_btn.setMinimumWidth(80)
        self.send_btn.clicked.connect(self.send_terminal_command)
        input_layout.addWidget(self.send_btn)

        # 历史按钮
        self.history_btn = QPushButton("📜 历史")
        self.history_btn.setMinimumWidth(80)
        self.history_btn.setToolTip("查看和选择历史命令 (Ctrl+H)")
        self.history_btn.clicked.connect(self.show_command_history)
        input_layout.addWidget(self.history_btn)

        self.clear_terminal_btn = QPushButton("清屏")
        self.clear_terminal_btn.setMinimumWidth(80)
        self.clear_terminal_btn.clicked.connect(self.clear_terminal)
        input_layout.addWidget(self.clear_terminal_btn)

        terminal_layout.addWidget(input_container)

        self.tabs.addTab(terminal_widget, "🖥️ 远程终端")

    def setup_file_transfer_tab(self):
        """设置文件传输标签页"""
        file_widget = QWidget()
        file_layout = QVBoxLayout(file_widget)
        file_layout.setSpacing(15)

        # 文件选择区域
        file_select_group = QGroupBox("文件选择")
        file_select_layout = QVBoxLayout()

        # 本地文件
        local_container = QWidget()
        local_layout = QHBoxLayout(local_container)
        local_layout.setContentsMargins(0, 0, 0, 0)

        local_layout.addWidget(QLabel("本地文件:"))
        self.file_path_input = QLineEdit()
        self.file_path_input.setPlaceholderText("选择要上传的文件...")
        local_layout.addWidget(self.file_path_input)

        self.browse_btn = QPushButton("浏览...")
        self.browse_btn.setMinimumWidth(100)
        self.browse_btn.clicked.connect(self.browse_file)
        local_layout.addWidget(self.browse_btn)

        file_select_layout.addWidget(local_container)

        # 目标路径
        target_container = QWidget()
        target_layout = QHBoxLayout(target_container)
        target_layout.setContentsMargins(0, 0, 0, 0)

        target_layout.addWidget(QLabel("目标路径:"))
        self.target_path_input = QLineEdit()
        self.target_path_input.setText("/tmp")
        self.target_path_input.setPlaceholderText("Linux服务器上的目标目录...")
        target_layout.addWidget(self.target_path_input)

        self.browse_remote_btn = QPushButton("浏览远程...")
        self.browse_remote_btn.setMinimumWidth(100)
        self.browse_remote_btn.clicked.connect(self.browse_remote_dir)
        target_layout.addWidget(self.browse_remote_btn)

        file_select_layout.addWidget(target_container)

        file_select_group.setLayout(file_select_layout)
        file_layout.addWidget(file_select_group)

        # 上传按钮
        self.upload_btn = QPushButton("📤 开始上传")
        self.upload_btn.setMinimumHeight(40)
        self.upload_btn.clicked.connect(self.upload_file)
        file_layout.addWidget(self.upload_btn)

        # 进度区域
        progress_group = QGroupBox("传输进度")
        progress_layout = QVBoxLayout()

        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        progress_layout.addWidget(self.progress_bar)

        self.progress_label = QLabel("等待上传...")
        self.progress_label.setAlignment(Qt.AlignCenter)
        progress_layout.addWidget(self.progress_label)

        progress_group.setLayout(progress_layout)
        file_layout.addWidget(progress_group)

        # 传输日志
        log_group = QGroupBox("传输日志")
        log_layout = QVBoxLayout()

        self.transfer_log = QTextEdit()
        self.transfer_log.setReadOnly(True)
        self.transfer_log.setMaximumHeight(200)
        log_layout.addWidget(self.transfer_log)

        log_group.setLayout(log_layout)
        file_layout.addWidget(log_group)

        file_layout.addStretch()

        self.tabs.addTab(file_widget, "📁 文件传输")

    def setup_about_tab(self):
        """设置关于标签页"""
        about_widget = QWidget()
        about_layout = QVBoxLayout(about_widget)
        about_layout.setAlignment(Qt.AlignCenter)

        # Logo/标题
        title = QLabel("FlashControler")
        title.setFont(QFont("Arial", 28, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        about_layout.addWidget(title)

        # 副标题
        subtitle = QLabel("闪控 - Windows到Linux远程控制工具")
        subtitle.setFont(QFont("Arial", 12))
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #7f8c8d; margin-bottom: 20px;")
        about_layout.addWidget(subtitle)

        # 版本信息
        version_label = QLabel(f"版本: {__version__}")
        version_label.setFont(QFont("Arial", 11))
        version_label.setAlignment(Qt.AlignCenter)
        about_layout.addWidget(version_label)

        about_layout.addSpacing(30)

        # 功能介绍
        features_group = QGroupBox("主要功能")
        features_layout = QVBoxLayout()
        features_layout.setSpacing(10)

        features = [
            "🖥️  远程终端访问 - 直接控制Linux主机终端",
            "📁  快速文件传输 - 轻松上传文件到Linux服务器",
            "🔒  安全认证 - 密码保护，确保连接安全",
            "🔄  自动更新 - 智能检测新版本",
            "🎨  美观界面 - 现代化的用户体验"
        ]

        for feature in features:
            label = QLabel(feature)
            label.setFont(QFont("Arial", 10))
            features_layout.addWidget(label)

        features_group.setLayout(features_layout)
        about_layout.addWidget(features_group)

        about_layout.addSpacing(20)

        # 检查更新按钮
        self.update_btn = QPushButton("🔄 检查更新")
        self.update_btn.setMinimumHeight(40)
        self.update_btn.setMinimumWidth(200)
        self.update_btn.clicked.connect(self.check_update)
        about_layout.addWidget(self.update_btn, alignment=Qt.AlignCenter)

        about_layout.addStretch()

        # 版权信息
        copyright_label = QLabel("© 2024 FlashControler | MIT License")
        copyright_label.setAlignment(Qt.AlignCenter)
        copyright_label.setStyleSheet("color: #95a5a6; font-size: 9px;")
        about_layout.addWidget(copyright_label)

        self.tabs.addTab(about_widget, "ℹ️ 关于")

    def apply_styles(self):
        """应用样式"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f6fa;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #dcdde1;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 5px 0 5px;
                color: #2c3e50;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
            QLineEdit {
                border: 2px solid #dcdde1;
                border-radius: 5px;
                padding: 8px;
                background-color: white;
                font-size: 11px;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
            QTabWidget::pane {
                border: 2px solid #dcdde1;
                border-radius: 5px;
                background-color: white;
                top: -1px;
            }
            QTabBar::tab {
                background-color: #ecf0f1;
                border: 2px solid #dcdde1;
                border-bottom: none;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
                padding: 10px 20px;
                margin-right: 2px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 2px solid white;
            }
            QTabBar::tab:hover {
                background-color: #d5dbdb;
            }
            QProgressBar {
                border: 2px solid #dcdde1;
                border-radius: 5px;
                text-align: center;
                height: 25px;
                background-color: white;
            }
            QProgressBar::chunk {
                background-color: #2ecc71;
                border-radius: 3px;
            }
            QTextEdit {
                border: 2px solid #dcdde1;
                border-radius: 5px;
                padding: 5px;
                background-color: white;
            }
        """)

    def setup_callbacks(self):
        """设置回调函数 - 使用信号来确保线程安全"""
        # 使用 lambda 来发射信号，而不是直接调用方法
        self.connection.register_callback('terminal_output', lambda output: self.terminal_output_signal.emit(self._process_output(output)))
        self.connection.register_callback('disconnected', lambda: self.disconnected_signal.emit())
        self.connection.register_callback('file_progress', lambda p, s, t: self.file_progress_signal.emit(p, s, t))

    def setup_signals(self):
        """连接信号到槽函数"""
        self.terminal_output_signal.connect(self.append_terminal_output)
        self.disconnected_signal.connect(self.on_disconnected)
        self.file_progress_signal.connect(self.on_file_progress)

    def _process_output(self, output):
        """处理输出数据（在接收线程中调用）"""
        if isinstance(output, bytes):
            try:
                output = output.decode('utf-8')
            except UnicodeDecodeError:
                try:
                    output = output.decode('gbk')
                except UnicodeDecodeError:
                    output = output.decode('utf-8', errors='replace')

        # 过滤ANSI转义序列
        return self.strip_ansi_codes(output)

    def toggle_connection(self):
        """切换连接状态"""
        if not self.connection.connected:
            host = self.host_input.text().strip()
            port_text = self.port_input.text().strip()
            password = self.password_input.text()

            if not host or not port_text:
                QMessageBox.warning(self, "输入错误", "请输入服务器地址和端口")
                return

            try:
                port = int(port_text)
            except ValueError:
                QMessageBox.warning(self, "输入错误", "端口必须是数字")
                return

            self.status_label.setText("连接中...")
            self.status_label.setStyleSheet("color: #f39c12; font-weight: bold;")
            self.status_indicator.setStyleSheet("color: #f39c12; font-size: 16px;")
            self.connect_btn.setEnabled(False)

            # 在后台线程连接
            self.conn_thread = ConnectionThread(self.connection, host, port, password)
            self.conn_thread.result.connect(self.on_connect_result)
            self.conn_thread.start()
        else:
            self.connection.disconnect()
            self.on_disconnected()

    def on_connect_result(self, success, message):
        """连接结果处理"""
        self.connect_btn.setEnabled(True)

        if success:
            self.status_label.setText("已连接")
            self.status_label.setStyleSheet("color: #27ae60; font-weight: bold;")
            self.status_indicator.setStyleSheet("color: #27ae60; font-size: 16px;")
            self.connect_btn.setText("断开连接")
            self.connect_btn.setStyleSheet("""
                QPushButton {
                    background-color: #e74c3c;
                }
                QPushButton:hover {
                    background-color: #c0392b;
                }
            """)

            # 保存连接信息
            self.config.set('client', 'last_host', self.host_input.text())
            self.config.set('client', 'last_port', int(self.port_input.text()))

            self.append_terminal_output(
                f"\n{'='*60}\n"
                f"已连接到 {self.host_input.text()}:{self.port_input.text()}\n"
                f"{'='*60}\n"
            )
        else:
            self.status_label.setText("未连接")
            self.status_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
            self.status_indicator.setStyleSheet("color: #e74c3c; font-size: 16px;")
            QMessageBox.critical(self, "连接失败", message)

    def on_disconnected(self):
        """断开连接回调"""
        self.status_label.setText("未连接")
        self.status_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
        self.status_indicator.setStyleSheet("color: #e74c3c; font-size: 16px;")
        self.connect_btn.setText("连接")
        self.connect_btn.setStyleSheet("")
        self.append_terminal_output(
            f"\n{'='*60}\n"
            f"连接已断开\n"
            f"{'='*60}\n"
        )

    def send_terminal_command(self):
        """发送终端命令"""
        if not self.connection.connected:
            QMessageBox.warning(self, "未连接", "请先连接到服务器")
            return

        command = self.terminal_input.text()
        if command:
            # 添加到命令历史
            self.terminal_input.add_to_history(command)

            if not command.endswith('\n'):
                command += '\n'

            self.connection.send_terminal_input(command)
            self.terminal_input.clear()

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

    def append_terminal_output(self, text):
        """追加终端输出（在主线程中调用）"""
        self.terminal_output.moveCursor(QTextCursor.End)
        self.terminal_output.insertPlainText(text)
        self.terminal_output.moveCursor(QTextCursor.End)

    def clear_terminal(self):
        """清空终端"""
        self.terminal_output.clear()

    def show_command_history(self):
        """显示命令历史对话框"""
        self.terminal_input.show_history_dialog()

    def browse_file(self):
        """浏览文件"""
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "选择要上传的文件",
            "",
            "所有文件 (*.*)"
        )
        if filename:
            self.file_path_input.setText(filename)

    def browse_remote_dir(self):
        """浏览远程目录"""
        if not self.connection.connected:
            QMessageBox.warning(self, "未连接", "请先连接到服务器")
            return

        dialog = RemoteDirDialog(self.connection, self)
        if dialog.exec_() == QDialog.Accepted:
            selected_path = dialog.get_selected_path()
            if selected_path:
                self.target_path_input.setText(selected_path)

    def upload_file(self):
        """上传文件"""
        if not self.connection.connected:
            QMessageBox.warning(self, "未连接", "请先连接到服务器")
            return

        file_path = self.file_path_input.text()
        target_path = self.target_path_input.text()

        if not file_path or not os.path.exists(file_path):
            QMessageBox.warning(self, "文件错误", "请选择有效的文件")
            return

        if not target_path:
            QMessageBox.warning(self, "路径错误", "请输入目标路径")
            return

        self.upload_btn.setEnabled(False)
        self.progress_bar.setValue(0)
        self.progress_label.setText("准备上传...")

        # 在后台线程上传
        self.upload_thread = UploadThread(self.connection, file_path, target_path)
        self.upload_thread.result.connect(self.on_upload_complete)
        self.upload_thread.start()

        self.log_transfer(f"开始上传: {os.path.basename(file_path)}")

    def on_upload_complete(self, success, message):
        """上传完成"""
        self.upload_btn.setEnabled(True)

        if success:
            self.log_transfer(f"✓ 上传成功: {message}")
            QMessageBox.information(self, "上传成功", message)
            self.progress_bar.setValue(100)
            self.progress_label.setText("上传完成!")
        else:
            self.log_transfer(f"✗ 上传失败: {message}")
            QMessageBox.critical(self, "上传失败", message)
            self.progress_label.setText("上传失败!")

    def on_file_progress(self, progress, sent, total):
        """文件传输进度回调"""
        self.progress_bar.setValue(int(progress))
        self.progress_label.setText(
            f"正在上传: {progress:.1f}% ({self.format_bytes(sent)} / {self.format_bytes(total)})"
        )

    def format_bytes(self, bytes_num):
        """格式化字节数"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_num < 1024.0:
                return f"{bytes_num:.2f} {unit}"
            bytes_num /= 1024.0
        return f"{bytes_num:.2f} TB"

    def log_transfer(self, message):
        """记录传输日志"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.transfer_log.append(f"[{timestamp}] {message}")

    def check_update(self):
        """检查更新"""
        self.update_btn.setEnabled(False)
        self.update_btn.setText("🔄 检查中...")

        self.update_check_thread = UpdateCheckThread(self.update_manager)
        self.update_check_thread.result.connect(self.on_update_checked)
        self.update_check_thread.start()

    def on_update_checked(self, update_info):
        """更新检查完成"""
        self.update_btn.setEnabled(True)
        self.update_btn.setText("🔄 检查更新")

        if update_info is None:
            QMessageBox.critical(self, "检查更新失败", "无法连接到更新服务器，请检查网络连接")
        elif update_info.get('has_update'):
            reply = QMessageBox.question(
                self,
                "发现新版本",
                f"发现新版本 {update_info['latest_version']}\n"
                f"当前版本 {update_info['current_version']}\n\n"
                f"是否前往下载页面？",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                import webbrowser
                webbrowser.open(update_info['download_url'])
        else:
            QMessageBox.information(
                self,
                "已是最新版本",
                f"当前版本 {update_info['current_version']} 已是最新版本"
            )


def main():
    """主函数"""
    app = QApplication(sys.argv)

    # 设置应用程序样式
    app.setStyle('Fusion')

    window = FlashClientGUI()
    window.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
