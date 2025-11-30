# FlashControler

闪控 - Windows到Linux的远程控制工具，支持远程终端和快速文件传输。

## ✨ 功能特性

- **远程终端访问**：在Windows客户端直接连接并控制Linux主机的终端
  - ⌨️ **命令历史记忆**：↑↓箭头键快速切换历史命令
  - 📜 **历史选择对话框**：Ctrl+H从列表选择历史命令
  - 自动保存最近100条命令，智能去重
- **快速文件传输**：轻松将文件从Windows上传到Linux的指定目录
  - 支持远程目录浏览
  - 实时传输进度显示
- **IP黑名单系统**：防止暴力破解和恶意连接
  - 🔒 认证失败10次自动封锁IP
  - 📊 实时显示连接和认证状态
  - 🛠️ 支持手动封锁/解锁IP
- **自动更新系统**：检测新版本并提示用户更新
- **安全认证**：密码保护的连接，确保安全性
- **现代化GUI**：PyQt5美观界面，扁平设计
- **多线程架构**：界面流畅不卡顿

## 🚀 快速开始

### 1. 安装

```bash
# 克隆仓库
git clone https://github.com/opzc35/FlashControler.git
cd FlashControler

# 安装依赖
pip install -r requirements.txt
```

### 2. 启动服务端（Linux）

```bash
python start_server.py
```

默认配置：
- 端口：9999
- 密码：flashcontrol123

### 3. 启动客户端（Windows）

```bash
python start_client.py
```

输入服务器IP、端口和密码即可连接。

## 📦 系统要求

### 服务端（Linux）
- Python 3.7+
- Linux操作系统（支持pty）

### 客户端（Windows）
- Python 3.7+
- Windows 7/10/11
- PyQt5

## ⚙️ 配置说明

配置文件：`config/settings.json`

### 服务端配置（server）

| 配置项 | 说明 | 默认值 |
|-------|------|--------|
| `host` | 监听地址 | "0.0.0.0" |
| `port` | 监听端口 | 9999 |
| `password` | 连接密码 | "flashcontrol123" |

### 客户端配置（client）

| 配置项 | 说明 | 默认值 |
|-------|------|--------|
| `last_host` | 上次连接的服务器IP地址<br>自动保存，方便下次使用 | "" |
| `last_port` | 上次连接的端口号<br>自动保存 | 9999 |

### 更新配置（update）

| 配置项 | 说明 | 默认值 |
|-------|------|--------|
| `check_on_startup` | 启动时是否自动检查更新 | true |
| `update_url` | 更新检查的API地址 | opzc35/FlashControler |

> **注意**：版本号和更新URL现在存储在代码中（`common/version.py`），不再需要在配置文件中设置。

### 终端配置（terminal）- 仅Linux服务端使用

| 配置项 | 说明 | 默认值 |
|-------|------|--------|
| `shell` | 使用的Shell程序路径 | "/bin/bash" |
| `encoding` | 终端编码 | "utf-8" |

## 🎯 使用指南

### 远程终端

1. 连接到服务器后，在终端窗口输入命令
2. 使用 ↑↓ 键浏览历史命令
3. 使用 Ctrl+H 打开历史命令选择对话框
4. Enter 执行命令

### 文件上传

1. 点击"选择文件"按钮
2. 浏览并选择远程目录
3. 点击"上传文件"
4. 查看传输日志和进度

### IP黑名单管理

服务端会自动记录认证失败次数，超过10次自动封锁IP。

**查看黑名单状态：**
```bash
python manage_ip.py status
```

**查看被封锁的IP：**
```bash
python manage_ip.py list
```

**解锁IP：**
```bash
python manage_ip.py unlock 192.168.1.100
```

**手动封锁IP：**
```bash
python manage_ip.py block 192.168.1.100
```

**服务端日志示例：**
```
[认证] ✓ IP 192.168.1.100 认证成功
[认证] ✗ IP 192.168.1.101 认证失败 (失败次数: 5/10)
[安全] 🔒 IP 192.168.1.101 已自动封锁（认证失败10次）
[安全]    使用 'python manage_ip.py unlock 192.168.1.101' 解锁
[安全] ❌ IP 192.168.1.101 已被封锁，拒绝连接
```

## 🛠️ 项目结构

```
FlashControler/
├── server/                 # 服务端模块
│   ├── server.py          # 主服务器
│   ├── terminal_handler.py # 终端处理
│   ├── file_handler.py     # 文件处理
│   └── ip_blacklist.py     # IP黑名单管理
├── client/                 # 客户端模块
│   ├── client_pyqt5.py    # PyQt5 GUI
│   ├── connection.py       # 网络连接
│   └── update_manager.py   # 更新管理
├── common/                 # 公共模块
│   ├── protocol.py         # 通信协议
│   ├── config.py           # 配置管理
│   └── version.py          # 版本信息
├── config/                 # 配置文件目录
│   └── ip_blacklist.json   # IP黑名单数据
├── start_server.py         # 服务端启动脚本
├── start_client.py         # 客户端启动脚本
├── manage_ip.py            # IP黑名单管理工具
└── README.md
```

## 🔧 开发

### 修改版本号

编辑 `common/version.py`：

```python
__version__ = "1.0.5"  # 修改这里
__version_info__ = (1, 0, 5)  # 同时修改这里
```

### 修改更新地址

编辑 `common/version.py`：

```python
GITHUB_REPO = "your-username/your-repo"
UPDATE_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
```

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📮 联系方式

- GitHub: [opzc35/FlashControler](https://github.com/opzc35/FlashControler)

---

**版本**: 1.0.4 | **更新**: 2024-11
