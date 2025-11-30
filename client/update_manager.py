"""
自动更新管理器
"""
import requests
import os
import sys
import json
from packaging import version

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.version import __version__ as DEFAULT_VERSION, UPDATE_URL


class UpdateManager:
    """自动更新管理器"""

    def __init__(self, current_version=None, update_url=None):
        # 如果没有指定版本号，使用代码中的默认版本号
        self.current_version = current_version or DEFAULT_VERSION
        # 如果没有指定更新URL，使用代码中的默认URL
        self.update_url = update_url or UPDATE_URL

    def check_update(self):
        """检查更新"""
        try:
            response = requests.get(self.update_url, timeout=10)
            if response.status_code == 200:
                release_data = response.json()
                latest_version = release_data.get('tag_name', '').lstrip('v')

                if version.parse(latest_version) > version.parse(self.current_version):
                    return {
                        'has_update': True,
                        'latest_version': latest_version,
                        'current_version': self.current_version,
                        'download_url': release_data.get('html_url'),
                        'release_notes': release_data.get('body', ''),
                        'published_at': release_data.get('published_at', '')
                    }
                else:
                    return {
                        'has_update': False,
                        'current_version': self.current_version,
                        'latest_version': latest_version
                    }
            else:
                return None

        except Exception as e:
            print(f"检查更新失败: {e}")
            return None

    def download_update(self, download_url, save_path):
        """下载更新"""
        try:
            response = requests.get(download_url, stream=True, timeout=30)
            if response.status_code == 200:
                total_size = int(response.headers.get('content-length', 0))
                downloaded = 0

                with open(save_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            progress = (downloaded / total_size * 100) if total_size > 0 else 0
                            yield progress, downloaded, total_size

                return True
            else:
                return False

        except Exception as e:
            print(f"下载更新失败: {e}")
            return False
