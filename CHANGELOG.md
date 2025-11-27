# 更新日志

本文档记录FlashControler的所有版本更新。

## [1.0.1] - 2024-11-27

### 修复
- 🐛 **修复终端中文乱码问题**
  - 服务端自动设置UTF-8 locale（zh_CN.UTF-8）
  - 服务端添加locale回退机制（en_US.UTF-8）
  - 客户端改进编码解码（UTF-8 → GBK → Replace）
  - 客户端使用支持中文的等宽字体
  - 详见 [ENCODING_FIX.md](ENCODING_FIX.md)

### 改进
- 📝 配置文件添加详细注释，标注服务端/客户端配置
- 📚 新增 [CONFIG.md](CONFIG.md) 配置详细说明文档
- 🌍 改善对中国大陆用户的支持

---

## [1.0.0] - 2024-11-27

### 首次发布

#### 新增功能
- ✨ 远程终端访问功能
  - 从Windows客户端直接连接Linux主机终端
  - 实时命令执行和输出显示
  - 支持所有标准bash命令

- ✨ 文件传输功能
  - Windows到Linux的文件上传
  - 可指定目标目录
  - 实时进度显示
  - 支持大文件传输

- ✨ 安全认证系统
  - 密码保护连接
  - 认证失败自动断开
  - 可配置密码

- ✨ 自动更新系统
  - 启动时自动检查更新
  - 从GitHub Releases获取版本信息
  - 一键跳转下载页面

- ✨ 双GUI界面选择
  - PyQt5现代化界面（推荐）
  - tkinter基础界面（备选）

#### 技术特性
- 基于TCP Socket的可靠通信
- 自定义二进制传输协议
- 多线程处理，不阻塞界面
- 模块化设计，易于扩展

#### 文档
- 完整的README.md
- 详细的INSTALL.md安装指南
- FEATURES.md功能特性说明
- 代码注释完善

---

## 开发计划

### [1.1.0] - 计划中

#### 计划功能
- [ ] 文件下载功能（Linux到Windows）
- [ ] 文件浏览器
- [ ] 批量文件传输
- [ ] 传输速度优化

### [1.2.0] - 计划中

#### 计划功能
- [ ] TLS/SSL加密通信
- [ ] 多终端会话支持
- [ ] 终端颜色支持（ANSI）
- [ ] 命令历史记录

### [2.0.0] - 远期计划

#### 计划功能
- [ ] 多服务器管理
- [ ] 系统监控面板
- [ ] 日志查看器
- [ ] 打包为独立可执行文件
- [ ] 跨平台支持（Mac）

---

## 版本号说明

使用语义化版本号（Semantic Versioning）：`主版本号.次版本号.修订号`

- **主版本号**：不兼容的API修改
- **次版本号**：向下兼容的功能新增
- **修订号**：向下兼容的问题修正

---

## 贡献

欢迎提交Issue和Pull Request！

参与方式：
1. Fork本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

---

## 反馈

如有问题或建议：
- 提交Issue: https://github.com/yourname/FlashControler/issues
- 发送邮件: your-email@example.com
