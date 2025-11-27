# 终端乱码问题修复说明

## 问题描述
在远程终端中显示中文或其他非ASCII字符时出现乱码。

## 原因分析
1. Linux服务端未设置正确的locale环境变量
2. 终端未使用UTF-8编码
3. 客户端字体不支持中文显示
4. 数据传输过程中编码处理不当

## 解决方案

### 1. 服务端修复（server/terminal_handler.py）

#### 设置环境变量
```python
# 创建环境变量，强制使用UTF-8
env = os.environ.copy()
env['LANG'] = 'zh_CN.UTF-8'
env['LC_ALL'] = 'zh_CN.UTF-8'
env['TERM'] = 'xterm-256color'
```

#### Locale回退机制
```python
# 如果系统不支持中文locale，自动回退到英文UTF-8
try:
    locale.setlocale(locale.LC_ALL, 'zh_CN.UTF-8')
except:
    env['LANG'] = 'en_US.UTF-8'
    env['LC_ALL'] = 'en_US.UTF-8'
```

#### 使用登录Shell
```python
# 使用 --login 参数，加载完整的shell环境
subprocess.Popen(['/bin/bash', '--login'], env=env, ...)
```

### 2. 客户端修复（PyQt5版本）

#### 多重编码尝试
```python
try:
    # 1. 优先UTF-8
    output = output.decode('utf-8')
except UnicodeDecodeError:
    try:
        # 2. 尝试GBK（中文Windows）
        output = output.decode('gbk')
    except UnicodeDecodeError:
        # 3. 替换模式（最后手段）
        output = output.decode('utf-8', errors='replace')
```

#### 使用支持中文的字体
```python
terminal_font = QFont()
terminal_font.setStyleHint(QFont.Monospace)
terminal_font.setFamily("Microsoft YaHei Mono, Consolas, Monaco, Courier New")
```

### 3. Linux系统配置

#### 检查系统locale
```bash
# 查看当前locale
locale

# 查看可用locale
locale -a

# 如果没有中文locale，安装它
sudo apt install language-pack-zh-hans  # Ubuntu/Debian
sudo yum install glibc-langpack-zh      # CentOS/RHEL

# 生成locale
sudo locale-gen zh_CN.UTF-8
sudo update-locale LANG=zh_CN.UTF-8
```

#### 配置系统默认locale
编辑 `/etc/default/locale`:
```
LANG="zh_CN.UTF-8"
LC_ALL="zh_CN.UTF-8"
```

重启或重新登录生效。

## 测试方法

### 测试1：中文文件名
```bash
# 在服务器端创建中文文件
touch 测试文件.txt
echo "这是中文内容" > 测试文件.txt

# 在客户端终端执行
ls
cat 测试文件.txt
```

应该能正确显示中文文件名和内容。

### 测试2：中文输出
```bash
# 执行包含中文的命令
echo "你好，世界！"
date  # 中文日期显示
```

### 测试3：系统信息
```bash
# 查看系统locale
locale
echo $LANG

# 查看当前目录（如果包含中文路径）
pwd
```

## 常见问题

### Q1: 仍然显示乱码怎么办？

**A**: 按顺序检查：

1. **服务端locale**：
   ```bash
   # 在服务器上执行
   locale | grep UTF-8
   # 应该看到 zh_CN.UTF-8 或 en_US.UTF-8
   ```

2. **客户端字体**：
   - Windows: 确保安装了中文字体
   - 字体设置：Microsoft YaHei, SimHei, 宋体等

3. **重启程序**：
   - 服务端和客户端都重启
   - 重新连接

### Q2: 部分字符显示为方框？

**A**: 字体问题，安装支持更多字符的字体：

**Windows**:
- 安装 Noto Sans CJK
- 或使用系统自带的 Microsoft YaHei

**Linux服务端**:
```bash
sudo apt install fonts-noto-cjk
```

### Q3: 英文系统如何显示中文？

**A**: 服务端配置会自动回退到 `en_US.UTF-8`，仍然支持UTF-8编码，可以正确处理中文，只是系统消息是英文。

### Q4: 不同地区的用户怎么办？

**A**: 修改配置文件 `config/settings.json`:

```json
{
    "terminal": {
        "shell": "/bin/bash",
        "encoding": "utf-8",  // 保持UTF-8
        "locale": "ja_JP.UTF-8"  // 日文用户可改为日文locale
    }
}
```

然后修改 `terminal_handler.py` 从配置文件读取locale。

## 技术细节

### UTF-8编码
- UTF-8是Unicode的一种实现方式
- 可以表示世界上所有的字符
- 兼容ASCII（前128个字符相同）
- 是Linux和Web的标准编码

### Locale系统
- `LANG`: 主要语言设置
- `LC_ALL`: 覆盖所有locale设置
- `LC_CTYPE`: 字符分类和转换
- 格式: `language_COUNTRY.ENCODING`
  - 例如: `zh_CN.UTF-8` (中文_中国.UTF-8)

### 字体渲染
- 等宽字体: 每个字符宽度相同，适合终端
- CJK字体: 支持中日韩统一表意文字
- Fallback机制: 字体不支持时自动使用其他字体

## 最佳实践

1. **服务端**:
   - 始终使用UTF-8编码
   - 设置合适的locale
   - 使用登录shell加载完整环境

2. **客户端**:
   - 多重编码尝试机制
   - 使用支持Unicode的字体
   - 合理的错误处理

3. **测试**:
   - 部署前测试中文显示
   - 测试不同locale环境
   - 测试各种特殊字符

## 更新日志

- 2024-11-27: 修复终端中文乱码问题
  - 服务端添加UTF-8 locale支持
  - 客户端改进编码处理
  - 添加中文字体支持
  - 添加locale回退机制

## 相关文档

- [README.md](README.md) - 项目说明
- [CONFIG.md](CONFIG.md) - 配置说明
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - 故障排除（如果有）
