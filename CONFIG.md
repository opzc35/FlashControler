# FlashControler 配置文件说明

## 配置文件结构

配置文件位于：`config/settings.json`

```json
{
    "_comment": "FlashControler 配置文件",
    "_note": "请根据使用场景（服务端/客户端）修改对应配置",

    "server": { /* 服务端配置 */ },
    "client": { /* 客户端配置 */ },
    "update": { /* 更新配置 - 双端共用 */ },
    "terminal": { /* 终端配置 */ }
}
```

---

## 配置详解

### 1. server - 服务端配置

**使用端：仅Linux服务端**

| 配置项 | 类型 | 默认值 | 说明 |
|-------|------|--------|------|
| `host` | string | "0.0.0.0" | 服务器监听地址<br>• `0.0.0.0` - 监听所有网卡（推荐）<br>• `127.0.0.1` - 仅本地访问<br>• 具体IP - 监听指定网卡 |
| `port` | int | 9999 | 服务器监听端口<br>• 1024-65535之间的数字<br>• 确保防火墙已开放此端口<br>• 客户端需要连接此端口 |
| `password` | string | "flashcontrol123" | 连接认证密码<br>• **必须修改默认值！**<br>• 建议使用强密码（12位以上）<br>• 客户端需要提供相同密码才能连接 |

**示例：**
```json
"server": {
    "host": "0.0.0.0",
    "port": 9999,
    "password": "MySecurePassword@2024"
}
```

**修改后需要：**
- 重启服务端程序
- 更新防火墙规则（如果修改了端口）
- 告知客户端新的端口和密码

---

### 2. client - 客户端配置

**使用端：仅Windows客户端**

| 配置项 | 类型 | 默认值 | 说明 |
|-------|------|--------|------|
| `last_host` | string | "" | 上次连接的服务器IP<br>• 自动保存，无需手动修改<br>• 下次启动自动填充到界面 |
| `last_port` | int | 9999 | 上次连接的端口<br>• 自动保存<br>• 下次启动自动填充 |
| `auto_reconnect` | bool | true | 自动重连功能<br>• **当前未实现，预留配置**<br>• 未来版本会支持断线自动重连 |

**示例：**
```json
"client": {
    "last_host": "192.168.1.100",
    "last_port": 9999,
    "auto_reconnect": true
}
```

**说明：**
- 这些配置会在客户端连接成功后**自动更新**
- 一般不需要手动修改
- 如果要清除历史记录，可以删除 `last_host` 的值

---

### 3. update - 更新配置

**使用端：客户端和服务端共用**

| 配置项 | 类型 | 默认值 | 说明 |
|-------|------|--------|------|
| `check_on_startup` | bool | true | 启动时检查更新<br>• `true` - 启动时自动检查<br>• `false` - 不自动检查（可手动检查） |
| `update_url` | string | GitHub API | 更新检查API地址<br>• 用于获取最新版本信息<br>• 一般不需要修改 |
| `current_version` | string | "1.0.0" | 当前程序版本号<br>• 用于版本比较<br>• **不要手动修改** |

**示例：**
```json
"update": {
    "check_on_startup": true,
    "update_url": "https://api.github.com/repos/yourname/FlashControler/releases/latest",
    "current_version": "1.0.0"
}
```

**说明：**
- 如果不希望启动时检查更新，设置 `check_on_startup` 为 `false`
- 仍可通过"关于"页面手动检查更新

---

### 4. terminal - 终端配置

**使用端：仅Linux服务端**

| 配置项 | 类型 | 默认值 | 说明 |
|-------|------|--------|------|
| `shell` | string | "/bin/bash" | Shell程序路径<br>• `/bin/bash` - Bash（默认）<br>• `/bin/zsh` - Zsh<br>• `/bin/sh` - POSIX Shell |
| `encoding` | string | "utf-8" | 终端编码格式<br>• `utf-8` - UTF-8（推荐）<br>• `gbk` - 中文GBK（Windows）<br>• `ascii` - ASCII |

**示例：**
```json
"terminal": {
    "shell": "/bin/bash",
    "encoding": "utf-8"
}
```

**说明：**
- 如果你使用zsh，可以改为 `"/bin/zsh"`
- 修改后需要重启服务端

---

## 配置场景示例

### 场景1：基本使用（内网）

**服务端配置：**
```json
{
    "server": {
        "host": "0.0.0.0",
        "port": 9999,
        "password": "MyPassword123!"
    },
    "terminal": {
        "shell": "/bin/bash",
        "encoding": "utf-8"
    }
}
```

**客户端配置：**
```json
{
    "client": {
        "last_host": "192.168.1.100",
        "last_port": 9999
    }
}
```

### 场景2：使用自定义端口

**服务端配置：**
```json
{
    "server": {
        "host": "0.0.0.0",
        "port": 8888,  // 自定义端口
        "password": "MyPassword123!"
    }
}
```

**防火墙设置：**
```bash
sudo ufw allow 8888  # Ubuntu/Debian
sudo firewall-cmd --add-port=8888/tcp --permanent  # CentOS/RHEL
sudo firewall-cmd --reload
```

### 场景3：仅本地测试

**服务端配置：**
```json
{
    "server": {
        "host": "127.0.0.1",  // 仅本地访问
        "port": 9999,
        "password": "test123"
    }
}
```

**客户端配置：**
```json
{
    "client": {
        "last_host": "127.0.0.1",  // 连接本地
        "last_port": 9999
    }
}
```

### 场景4：关闭自动更新检查

**双端配置：**
```json
{
    "update": {
        "check_on_startup": false  // 不自动检查更新
    }
}
```

---

## 配置文件管理

### 备份配置

```bash
# Linux
cp config/settings.json config/settings.json.backup

# Windows
copy config\settings.json config\settings.json.backup
```

### 重置为默认配置

删除配置文件，程序会自动创建默认配置：

```bash
# Linux
rm config/settings.json

# Windows
del config\settings.json
```

### 多环境配置（高级）

可以为不同环境创建不同配置文件：

```bash
config/
├── settings.json          # 默认配置
├── settings.dev.json      # 开发环境
├── settings.prod.json     # 生产环境
└── settings.test.json     # 测试环境
```

然后在启动时指定配置文件（需要修改代码支持）。

---

## 安全建议

### 密码强度

❌ **弱密码（不要使用）：**
- `123456`
- `password`
- `flashcontrol123`（默认密码）

✅ **强密码（推荐）：**
- `Fc@2024!SecurePwd`
- `My$ecure#Passw0rd`
- `FlashCtrl@2024!@#`

### 访问控制

1. **修改默认端口**：使用非标准端口（如8888而不是9999）
2. **防火墙规则**：仅允许特定IP访问
   ```bash
   # 仅允许特定IP访问9999端口
   sudo ufw allow from 192.168.1.0/24 to any port 9999
   ```

3. **定期更换密码**：建议每月更换一次密码

---

## 常见问题

### Q1: 修改配置后不生效？

**A**: 需要重启程序：
```bash
# 服务端
sudo systemctl restart flashcontrol
# 或
python3 start_server.py

# 客户端
# 直接重新启动客户端程序
```

### Q2: 配置文件格式错误？

**A**: 确保JSON格式正确：
- 所有字符串使用双引号 `""`
- 布尔值使用小写 `true`/`false`
- 数字不要加引号
- 最后一项后面不要有逗号

可以使用在线JSON验证工具检查：https://jsonlint.com/

### Q3: 客户端和服务端可以共用配置文件吗？

**A**: 可以！程序会自动读取对应部分：
- 服务端只读取 `server` 和 `terminal` 部分
- 客户端只读取 `client` 部分
- `update` 部分双端都会读取

### Q4: 忘记密码怎么办？

**A**: 编辑配置文件重新设置：
```bash
nano config/settings.json
# 修改 server.password 字段
# 保存后重启服务端
```

---

## 相关文档

- [README.md](README.md) - 项目说明
- [QUICKSTART.md](QUICKSTART.md) - 快速开始
- [INSTALL.md](INSTALL.md) - 安装指南
- [FEATURES.md](FEATURES.md) - 功能特性
