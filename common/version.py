"""
FlashControler 版本信息

此文件包含应用程序的版本号和相关元数据
"""

__version__ = "V1.1.1"
__version_info__ = (1, 1, 1)

# GitHub 仓库信息
GITHUB_REPO = "opzc35/FlashControler"
UPDATE_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"

# 版本号说明：
# 主版本号.次版本号.修订号
# 例如：1.0.4 表示第1个主版本，第0个次版本，第4次修订

# 更新日志（最近更新）
CHANGELOG = """
V1.1.1 (2025-12)
- 新增自定义留言功能：已登录客户端可设置登录失败时的提示信息
- 安全增强：服务端显示每次认证尝试的密码
- 新增文件下载功能（Linux到Windows）
- 新增文件浏览器，支持可视化浏览远程文件系统
- 支持批量文件下载，可多选文件
- 传输速度优化，数据块大小提升至64KB
- 服务端增加IP黑名单功能，可以手动封锁和过多尝试自动封锁
"""
