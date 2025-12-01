"""
FlashControler 版本信息

此文件包含应用程序的版本号和相关元数据
"""

__version__ = "1.1.0"
__version_info__ = (1, 1, 0)

# GitHub 仓库信息
GITHUB_REPO = "opzc35/FlashControler"
UPDATE_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"

# 版本号说明：
# 主版本号.次版本号.修订号
# 例如：1.0.4 表示第1个主版本，第0个次版本，第4次修订

# 更新日志（最近更新）
CHANGELOG = """
v1.1.0 (2024-11)
- 新增文件下载功能（Linux到Windows）
- 新增文件浏览器，支持可视化浏览远程文件系统
- 支持批量文件下载，可多选文件
- 传输速度优化，数据块大小提升至64KB
- 服务端增加IP黑名单功能，可以手动封锁和过多尝试自动封锁
- 简化大量代码，完全删掉Tkinter版本
"""
