# FlashControler 安装指南

## Windows客户端安装

### 方式1：完整安装（推荐）

适合希望获得最佳用户体验的用户。

1. 安装Python 3.7或更高版本
   - 从 https://www.python.org/downloads/ 下载
   - 安装时勾选"Add Python to PATH"

2. 下载FlashControler
   ```bash
   git clone https://github.com/yourname/FlashControler.git
   cd FlashControler
   ```

3. 安装所有依赖
   ```bash
   pip install -r requirements.txt
   ```

4. 运行客户端
   ```bash
   python start_client_pyqt5.py
   ```

### 方式2：最小化安装

适合只需要基本功能的用户，或者无法安装PyQt5的环境。

1. 安装Python 3.7或更高版本

2. 下载FlashControler

3. 安装最小依赖
   ```bash
   pip install requests packaging
   ```

4. 运行客户端
   ```bash
   python client/client.py
   ```

注意：最小化安装使用tkinter（Python自带），界面较为简单。

### 方式3：打包为独立程序（未来支持）

将来会提供独立的.exe文件，无需安装Python即可运行。

## Linux服务端安装

1. 确保安装Python 3.7+
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip
   ```

2. 下载FlashControler
   ```bash
   git clone https://github.com/yourname/FlashControler.git
   cd FlashControler
   ```

3. 安装依赖（可选，服务端不需要GUI库）
   ```bash
   pip3 install requests packaging
   ```

4. 配置服务器
   编辑 `config/settings.json`，修改密码等设置

5. 运行服务器
   ```bash
   python3 start_server.py
   ```

6. 设置开机自启动（可选）
   创建systemd服务文件：
   ```bash
   sudo nano /etc/systemd/system/flashcontrol.service
   ```

   添加以下内容：
   ```ini
   [Unit]
   Description=FlashControler Server
   After=network.target

   [Service]
   Type=simple
   User=your_username
   WorkingDirectory=/path/to/FlashControler
   ExecStart=/usr/bin/python3 /path/to/FlashControler/start_server.py
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

   启用服务：
   ```bash
   sudo systemctl enable flashcontrol
   sudo systemctl start flashcontrol
   ```

## 界面对比

### PyQt5版本（推荐）
- ✅ 现代化的扁平设计
- ✅ 流畅的动画效果
- ✅ 更丰富的控件
- ✅ 更好的高DPI支持
- ✅ 可自定义主题
- ❌ 需要额外安装PyQt5

### tkinter版本（基础）
- ✅ 无需额外依赖
- ✅ 轻量级
- ✅ 跨平台兼容性好
- ❌ 界面较为简单
- ❌ 功能相对基础

## 故障排除

### PyQt5安装失败

如果遇到PyQt5安装问题：

**Windows:**
```bash
pip install PyQt5 -i https://pypi.tuna.tsinghua.edu.cn/simple
```

**Linux:**
```bash
sudo apt install python3-pyqt5
```

### 连接问题

1. 确认服务器正在运行
2. 检查防火墙设置
3. 确认IP地址和端口正确
4. 测试网络连通性：`ping server_ip`

### 权限问题（Linux）

如果上传文件时遇到权限错误：
```bash
# 确保目标目录有写入权限
chmod 755 /target/directory
```
