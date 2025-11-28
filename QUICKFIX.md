# 快速修复指南

本文档提供常见问题的快速解决方案。

## 问题1: 显示 `[?2004h` 等奇怪字符

### 症状
终端输出显示类似以下字符：
```
[?2004hubuntu@VM:~$
[0m[31m红色文本[0m
```

### 原因
这是ANSI转义序列（终端控制码），用于控制颜色、光标等，但GUI客户端未正确处理。

### 解决方案（已在V1.0.2修复）

**如果使用V1.0.2或更高版本**：
- 无需任何操作，已自动过滤

**如果使用旧版本**：
1. 更新到最新版本，或
2. 临时方案 - 在服务器端禁用：
   ```bash
   # 编辑 ~/.bashrc
   echo "bind 'set enable-bracketed-paste off'" >> ~/.bashrc
   source ~/.bashrc
   ```

---

## 问题2: 中文显示乱码

### 症状
中文显示为 `???` 或方框

### 解决方案
1. **服务端**（已在V1.0.1修复）：
   ```bash
   # 安装中文locale
   sudo apt install language-pack-zh-hans
   sudo locale-gen zh_CN.UTF-8
   ```

2. **客户端**：
   - Windows用户：确保安装了中文字体（Microsoft YaHei）
   - 已在V1.0.1自动处理编码

---

## 问题3: pip安装失败

### 症状
```
UnicodeDecodeError: 'gbk' codec can't decode byte
```

### 解决方案
```cmd
# Windows CMD
set PYTHONUTF8=1
python -m pip install --upgrade pip
pip install -r requirements.txt

# 或使用镜像源
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

---

## 问题4: PyQt5编译失败

### 症状
```
FileNotFoundError: [Errno 2] No such file or directory: '...PyQt5\\setup.py'
```

### 解决方案
```cmd
# 升级pip和构建工具
python -m pip install --upgrade pip setuptools wheel

# 重新安装
pip install -r requirements.txt
```

---

## 版本历史

- **V1.0.2** (2024-11-28): 修复ANSI转义序列显示
- **V1.0.1** (2024-11-27): 修复中文乱码
- **V1.0.0** (2024-11-27): 首次发布

---

## 获取帮助

如果问题仍未解决：
1. 查看 [ENCODING_FIX.md](ENCODING_FIX.md) 详细说明
2. 查看 [INSTALL.md](INSTALL.md) 安装指南
3. 提交Issue到GitHub仓库
