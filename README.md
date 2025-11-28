# FlashControler

闪控 - Windows到Linux的远程控制工具，支持远程终端和快速文件传输。

## 功能特性

- **远程终端访问**：在Windows客户端直接连接并控制Linux主机的终端
  - ⌨️ **命令历史记忆**：↑↓箭头键快速切换历史命令（V1.0.3新增）
  - 📜 **历史选择对话框**：点击按钮或Ctrl+H从列表选择（V1.0.3新增）
  - 自动保存最近100条命令，智能去重
- **快速文件传输**：轻松将文件从Windows上传到Linux的指定目录
- **自动更新系统**：检测新版本并提示用户更新
- **安全认证**：密码保护的连接，确保安全性
- **双GUI选择**：
  - PyQt5现代化界面（扁平设计，美观大方）
  - tkinter基础界面（轻量简洁，没啥优点）
- **实时进度**：文件传输和命令执行的实时反馈
- **多线程架构**：界面流畅不卡顿

## 界面预览

### PyQt5版本（推荐）
- 现代化扁平设计
- 彩色状态指示
- 实时进度条
- 分组布局清晰
- 支持高DPI显示

### tkinter版本
- 简洁实用
- 无需额外依赖
- 兼容性好
- 轻量快速

## 系统要求

### 服务端（Linux）
- Python 3.7+
- Linux操作系统（支持pty）

### 客户端（Windows）
- Python 3.7+
- Windows 7/10/11
- **推荐**: PyQt5（美观的现代化界面）
- **备选**: tkinter（Python自带，基础界面，强烈不推荐，不经常跟进）

## 安装

1. 克隆仓库：
```bash
git clone https://github.com/opzc35/FlashControler.git
cd FlashControler
```

2. 安装依赖：
```bash
# 基础版本（使用tkinter）
pip install requests packaging

# 推荐：安装完整版本（使用PyQt5，界面更美观）
pip install -r requirements.txt
```

3. 配置设置：
编辑 `config/settings.json` 文件，设置服务器密码和其他选项。

## 使用方法

### 启动服务端（Linux）

在Linux主机上运行：

```bash
python server/server.py
```

服务器将在 `0.0.0.0:9999` 上监听连接。

### 启动客户端（Windows）

在Windows机器上运行：

**方式1：使用PyQt5美化界面（推荐）**
```cmd
python start_client_pyqt5.py
```

**方式2：使用tkinter基础界面**
```cmd
python client/client.py
```

使用GUI界面：
1. 输入Linux服务器的IP地址和端口
2. 输入连接密码
3. 点击"连接"按钮
4. 使用"远程终端"标签页执行命令
   - 💡 **提示**：使用 ↑↓ 箭头键快速切换历史命令
   - 💡 **提示**：点击 📜 **历史** 按钮或按 **Ctrl+H** 从列表选择历史命令
5. 使用"文件传输"标签页上传文件

## 配置说明

`config/settings.json` 配置文件详细说明：

### 服务端配置（server）- 仅Linux服务端使用

| 配置项 | 说明 | 默认值 | 使用端 |
|-------|------|--------|--------|
| `host` | 服务器监听地址<br>0.0.0.0表示监听所有网卡 | "0.0.0.0" | **服务端** |
| `port` | 服务器监听端口<br>客户端需要连接此端口 | 9999 | **服务端** |
| `password` | 连接密码<br> **必须修改！** 客户端需要提供相同密码 | "flashcontrol123" | **服务端** |

### 客户端配置（client）- 仅Windows客户端使用

| 配置项 | 说明 | 默认值 | 使用端 |
|-------|------|--------|--------|
| `last_host` | 上次连接的服务器IP地址<br>自动保存，方便下次使用 | "" | **客户端** |
| `last_port` | 上次连接的端口号<br>自动保存 | 9999 | **客户端** |
| `auto_reconnect` | 是否自动重连<br>（暂未实现，预留） | true | **客户端** |

### 更新配置（update）- 客户端和服务端共用

| 配置项 | 说明 | 默认值 | 使用端 |
|-------|------|--------|--------|
| `check_on_startup` | 启动时是否自动检查更新 | true | **双端** |
| `update_url` | 更新检查的API地址<br>用于获取最新版本信息 | GitHub API | **双端** |
| `current_version` | 当前程序版本号 | "1.0.0" | **双端** |

### 终端配置（terminal）- 仅Linux服务端使用

| 配置项 | 说明 | 默认值 | 使用端 |
|-------|------|--------|--------|
| `shell` | 使用的Shell程序路径 | "/bin/bash" | **服务端** |
| `encoding` | 终端编码格式 | "utf-8" | **服务端** |

### 配置示例

**Linux服务端 - 最小配置：**
```json
{
    "server": {
        "host": "0.0.0.0",
        "port": 9999,
        "password": "your_secure_password_here"  // 务必修改！
    }
}
```

**Windows客户端 - 最小配置：**
```json
{
    "client": {
        "last_host": "192.168.1.100",  // 服务器IP
        "last_port": 9999
    }
}
```

### 配置文件位置

- **Linux**: `/path/to/FlashControler/config/settings.json`
- **Windows**: `C:\path\to\FlashControler\config\settings.json`

注意：客户端和服务端可以共用同一个配置文件，程序会自动读取对应部分

## 项目结构

```
FlashControler/
├── server/                  # Linux服务端
│   ├── __init__.py
│   ├── server.py            # 服务器主程序
│   ├── terminal_handler.py  # 终端处理器
│   └── file_handler.py      # 文件接收处理器
├── client/                  # Windows客户端
│   ├── __init__.py
│   ├── client.py            # 客户端主程序（tkinter版）
│   ├── client_pyqt5.py      # 客户端主程序（PyQt5美化版）
│   ├── connection.py        # 网络连接管理
│   └── update_manager.py    # 自动更新管理
├── common/                  # 共享模块
│   ├── __init__.py
│   ├── protocol.py          # 通信协议定义
│   └── config.py            # 配置管理
├── config/                  # 配置文件
│   └── settings.json        # 主配置文件
├── start_server.py          # Linux服务端启动脚本
├── start_client.py          # Windows客户端启动脚本（自适应）
├── start_client_pyqt5.py    # Windows客户端启动脚本（PyQt5优先）
├── requirements.txt         # Python依赖
├── README.md                # 项目说明
├── INSTALL.md               # 安装指南
├── QUICKSTART.md            # 快速开始
├── FEATURES.md              # 功能特性详解
├── CHANGELOG.md             # 更新日志
├── LICENSE                  # MIT许可证
└── .gitignore               # Git忽略文件
```

## 安全建议

1. **修改默认密码**：在 `config/settings.json` 中设置强密码
2. **防火墙配置**：确保服务器端口仅对信任的IP开放
3. **网络环境**：建议在内网或VPN环境中使用
4. **定期更新**：保持软件版本最新

## 常见问题

### Q: 连接失败怎么办？
A: 检查：
- Linux服务器是否正在运行
- 防火墙是否允许端口 9999
- IP地址和端口是否正确
- 密码是否匹配

### Q: 文件上传失败？
A: 确保：
- 目标路径在Linux上存在或有权限创建
- 文件大小不超过系统限制
- 网络连接稳定

### Q: 终端显示乱码？
A: 这是中文编码问题，已修复！
- **服务端**: 自动设置UTF-8 locale（zh_CN.UTF-8）
- **客户端**: 使用支持中文的字体
- **详细说明**: 查看 [ENCODING_FIX.md](ENCODING_FIX.md)

如果仍有问题：
```bash
# Linux服务器上检查locale
locale | grep UTF-8

# 如果没有，安装中文语言包
sudo apt install language-pack-zh-hans
sudo locale-gen zh_CN.UTF-8
```

### Q: 终端无输出？
A: 尝试：
- 发送简单命令如 `ls` 测试
- 检查网络连接
- 重新连接服务器

## 开发计划

### v1.1.0
- [ ] 文件下载功能（Linux到Windows）
- [ ] 文件浏览器
- [ ] 批量文件传输
- [ ] 传输断点续传

### v1.2.0
- [ ] TLS/SSL加密通信
- [ ] 多终端会话支持
- [ ] 终端颜色支持（ANSI转义序列）
- [ ] 命令历史和Tab补全

### v2.0.0
- [ ] 多服务器连接管理
- [ ] 系统监控面板
- [ ] 日志查看器
- [ ] 打包为独立可执行文件（.exe）
- [ ] 跨平台支持（macOS）

查看完整计划：[CHANGELOG.md](CHANGELOG.md)

## 文档

- 📖 [README.md](README.md) - 项目概述和基本使用
- 🚀 [QUICKSTART.md](QUICKSTART.md) - 5分钟快速开始
- 🔧 [INSTALL.md](INSTALL.md) - 详细安装指南
- ⚙️ [CONFIG.md](CONFIG.md) - 配置文件详细说明（服务端/客户端配置区分）
- ⌨️ [COMMAND_HISTORY.md](COMMAND_HISTORY.md) - 命令历史功能说明 **NEW**
- 🔤 [ENCODING_FIX.md](ENCODING_FIX.md) - 终端乱码修复说明（UTF-8中文支持）
- ⭐ [FEATURES.md](FEATURES.md) - 功能特性详解
- 📝 [CHANGELOG.md](CHANGELOG.md) - 版本更新日志
- 📄 [LICENSE](LICENSE) - MIT开源许可证

## 技术栈

**后端**
- Python 3.7+
- Socket网络编程
- pty伪终端
- threading多线程

**前端**
- PyQt5 - 现代化GUI（推荐）
- tkinter - 基础GUI（备选）

**依赖**
- requests - HTTP请求
- packaging - 版本管理

## 代码统计

- 总代码行数：~2000行
- Python文件：15个
- 模块化设计，易于维护和扩展

欢迎提交Issue和Pull Request！

## 许可证

MIT License

## 联系方式

如有问题或建议，请提交Issue。
