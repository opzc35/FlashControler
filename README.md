# FlashControler

闪控 - Windows到Linux的远程控制工具，支持远程终端和快速文件传输。

## 功能特性

- **远程终端访问**：在Windows客户端直接连接并控制Linux主机的终端
- **快速文件传输**：轻松将文件从Windows上传到Linux的指定目录
- **自动更新系统**：检测新版本并提示用户更新
- **安全认证**：密码保护的连接，确保安全性
- **双GUI选择**：
  - PyQt5现代化界面（扁平设计，美观大方）
  - tkinter基础界面（轻量简洁，无需额外依赖）
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
- **备选**: tkinter（Python自带，基础界面）

## 安装

1. 克隆仓库：
```bash
git clone https://github.com/yourname/FlashControler.git
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
```bash
python start_client_pyqt5.py
```

**方式2：使用tkinter基础界面**
```bash
python client/client.py
```

使用GUI界面：
1. 输入Linux服务器的IP地址和端口
2. 输入连接密码
3. 点击"连接"按钮
4. 使用"远程终端"标签页执行命令
5. 使用"文件传输"标签页上传文件

## 配置说明

`config/settings.json` 配置文件说明：

```json
{
    "server": {
        "host": "0.0.0.0",        // 服务器监听地址
        "port": 9999,              // 服务器端口
        "password": "your_password" // 连接密码（请修改）
    },
    "client": {
        "last_host": "",           // 上次连接的服务器地址
        "last_port": 9999,         // 上次连接的端口
        "auto_reconnect": true     // 是否自动重连
    },
    "update": {
        "check_on_startup": true,  // 启动时检查更新
        "update_url": "...",       // 更新检查URL
        "current_version": "1.0.0" // 当前版本
    }
}
```

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

### Q: 终端无输出？
A: 尝试：
- 发送简单命令如 `ls` 测试
- 检查终端编码设置
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
