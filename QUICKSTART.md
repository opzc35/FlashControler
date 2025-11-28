# FlashControler 快速开始

5分钟快速上手FlashControler！

## 快速部署

### Step 1: 准备环境

**Linux服务器（被控端）**
```bash
# 检查Python版本（需要3.7+）
python3 --version

# 如果没有安装Python
sudo apt update && sudo apt install python3 python3-pip
```

**Windows客户端（控制端）**
- 确保已安装Python 3.7+
- 下载地址：https://www.python.org/downloads/

### Step 2: 下载项目

**在Linux服务器和Windows客户端都执行：**

```bash
git clone https://github.com/opzc35/FlashControler.git
cd FlashControler
```

如果没有git，可以直接下载ZIP：
https://github.com/opzc35/FlashControler/archive/main.zip

### Step 3: 配置服务器

**在Linux服务器上：**

1. 编辑配置文件：
```bash
nano config/settings.json
```

2. 修改服务端配置（**重要！**）：
```json
{
    "server": {
        "_comment": "【Linux服务端配置】仅服务端使用",
        "host": "0.0.0.0",              // 监听所有网卡（通常不需要改）
        "port": 9999,                    // 监听端口（可自定义）
        "password": "your_secure_password_here"  // ⚠️ 必须修改这个密码！
    }
}
```

**配置说明：**
- `host`: 服务器监听地址，`0.0.0.0` 表示监听所有网络接口
- `port`: 服务器端口，客户端将连接此端口
- `password`: 连接密码，**务必修改为强密码**

3. 保存并退出（Ctrl+O, Enter, Ctrl+X）

### Step 4: 启动服务器

**在Linux服务器上：**

```bash
python3 start_server.py
```

看到以下输出表示成功：
```
[FlashControler] 服务器启动成功
[FlashControler] 监听地址: 0.0.0.0:9999
[FlashControler] 等待客户端连接...
```

### Step 5: 安装客户端依赖

**在Windows客户端上：**

**方式A：完整版（推荐，界面美观）**
```bash
pip install -r requirements.txt
```

**方式B：精简版（界面简单但够用）**
```bash
pip install requests packaging
```

### Step 6: 启动客户端

**在Windows客户端上：**

**方式A：美化界面（如果安装了PyQt5）**
```bash
python start_client_pyqt5.py
```

**方式B：基础界面**
```bash
python start_client.py
```

### Step 7: 连接到服务器

1. 在客户端界面输入（这些是**客户端连接参数**，不是配置文件）：
   - **服务器地址**：Linux服务器的IP地址（如：192.168.1.100）
   - **端口**：9999（与服务端配置的port一致）
   - **密码**：你在Step 3设置的服务端密码

2. 点击"连接"按钮

3. 看到"已连接"提示即成功！

**说明：**
- 客户端会自动保存上次连接的地址到 `client.last_host` 和 `client.last_port`
- 下次启动时会自动填充这些信息

## 快速测试

### 测试1：终端功能

1. 切换到"远程终端"标签页
2. 在命令框输入：`ls -la`
3. 按Enter或点击"发送"
4. 应该看到Linux服务器的文件列表

### 测试2：文件传输

1. 切换到"文件传输"标签页
2. 点击"浏览"选择一个测试文件
3. 目标路径输入：`/tmp`
4. 点击"开始上传"
5. 观察进度条，完成后会提示成功

在Linux服务器上验证：
```bash
ls -lh /tmp/your_file_name
```

## 常见问题快速解决

### Q1: 无法连接到服务器

**检查清单：**
```bash
# 1. 服务器是否在运行？
# Linux上应该能看到服务器进程

# 2. 网络是否通畅？
ping 192.168.1.100  # 替换为你的服务器IP

# 3. 防火墙是否开放端口？
# Ubuntu/Debian:
sudo ufw allow 9999

# CentOS/RHEL:
sudo firewall-cmd --add-port=9999/tcp --permanent
sudo firewall-cmd --reload

# 4. 密码是否正确？
# 检查config/settings.json
```

### Q2: PyQt5安装失败

```bash
# 使用国内镜像加速
pip install PyQt5 -i https://pypi.tuna.tsinghua.edu.cn/simple

# 或者直接用基础版
python client/client.py
```

### Q3: 文件上传失败

```bash
# 确保目标目录存在且有权限
mkdir -p /target/path
chmod 755 /target/path
```

## 进阶使用

### 设置开机自启（Linux服务器）

1. 创建systemd服务：
```bash
sudo nano /etc/systemd/system/flashcontrol.service
```

2. 添加内容：
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

3. 启用服务：
```bash
sudo systemctl enable flashcontrol
sudo systemctl start flashcontrol
sudo systemctl status flashcontrol
```

### 修改默认端口

编辑 `config/settings.json`：
```json
{
    "server": {
        "port": 8888  // 改为你想要的端口
    }
}
```

记得同时修改防火墙规则！

### 多服务器管理（客户端）

客户端会记住上次连接的服务器地址，如需连接不同服务器：
1. 断开当前连接
2. 输入新的服务器地址
3. 点击连接

## 安全建议

1. **修改默认密码**：第一次使用务必修改密码
2. **使用强密码**：至少12位，包含大小写字母、数字、符号
3. **限制访问IP**：如可能，配置防火墙只允许特定IP访问
4. **定期更新**：关注项目更新，及时升级
5. **内网使用**：建议在内网或VPN环境使用

## 获取帮助

- 📖 完整文档：README.md
- 🔧 安装指南：INSTALL.md
- ⭐ 功能说明：FEATURES.md
- 📝 更新日志：CHANGELOG.md
- 🐛 问题反馈：https://github.com/yourname/FlashControler/issues

## 下一步

恭喜你已经成功运行FlashControler！

继续探索：
- 尝试更多Linux命令
- 上传不同类型的文件
- 查看传输日志
- 检查软件更新

享受使用FlashControler的便利吧！ 🚀
