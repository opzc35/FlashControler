"""
IP黑名单管理模块
用于防止暴力破解和恶意连接
"""
import json
import os
from datetime import datetime
from threading import Lock


class IPBlacklist:
    """IP黑名单管理器"""

    def __init__(self, blacklist_file="config/ip_blacklist.json", max_failures=10):
        """
        初始化IP黑名单管理器

        Args:
            blacklist_file: 黑名单存储文件路径
            max_failures: 最大失败次数，超过后自动封锁
        """
        self.blacklist_file = blacklist_file
        self.max_failures = max_failures
        self.lock = Lock()

        # 黑名单数据结构：
        # {
        #     "192.168.1.100": {
        #         "blocked": True,
        #         "fail_count": 12,
        #         "blocked_time": "2024-11-30 10:30:00",
        #         "reason": "认证失败次数过多"
        #     }
        # }
        self.blacklist = {}

        self.load()

    def check_blocked(self, ip):
        """
        检查IP是否被封锁

        Args:
            ip: IP地址

        Returns:
            tuple: (是否被封锁, 封锁原因)
        """
        with self.lock:
            if ip in self.blacklist and self.blacklist[ip].get('blocked', False):
                reason = self.blacklist[ip].get('reason', '未知原因')
                return True, reason
            return False, None

    def record_auth_failure(self, ip):
        """
        记录认证失败

        Args:
            ip: IP地址

        Returns:
            bool: 是否触发自动封锁
        """
        with self.lock:
            if ip not in self.blacklist:
                self.blacklist[ip] = {
                    'blocked': False,
                    'fail_count': 0,
                    'blocked_time': None,
                    'reason': None
                }

            self.blacklist[ip]['fail_count'] += 1
            fail_count = self.blacklist[ip]['fail_count']

            # 检查是否达到自动封锁阈值
            if fail_count >= self.max_failures and not self.blacklist[ip]['blocked']:
                self.blacklist[ip]['blocked'] = True
                self.blacklist[ip]['blocked_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.blacklist[ip]['reason'] = f"认证失败{fail_count}次，超过阈值{self.max_failures}"
                self.save()
                return True

            self.save()
            return False

    def record_auth_success(self, ip):
        """
        记录认证成功，清零失败计数

        Args:
            ip: IP地址
        """
        with self.lock:
            if ip in self.blacklist:
                # 认证成功，清零失败计数
                self.blacklist[ip]['fail_count'] = 0
                # 如果不是手动封锁的，可以解除封锁
                if not self.blacklist[ip].get('manual_block', False):
                    self.blacklist[ip]['blocked'] = False
                    self.blacklist[ip]['reason'] = None
                self.save()

    def block_ip(self, ip, reason="手动封锁"):
        """
        手动封锁IP

        Args:
            ip: IP地址
            reason: 封锁原因
        """
        with self.lock:
            if ip not in self.blacklist:
                self.blacklist[ip] = {
                    'blocked': False,
                    'fail_count': 0,
                    'blocked_time': None,
                    'reason': None
                }

            self.blacklist[ip]['blocked'] = True
            self.blacklist[ip]['manual_block'] = True
            self.blacklist[ip]['blocked_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.blacklist[ip]['reason'] = reason
            self.save()

    def unblock_ip(self, ip):
        """
        手动解锁IP

        Args:
            ip: IP地址

        Returns:
            bool: 是否成功解锁
        """
        with self.lock:
            if ip in self.blacklist:
                self.blacklist[ip]['blocked'] = False
                self.blacklist[ip]['fail_count'] = 0
                self.blacklist[ip]['manual_block'] = False
                self.blacklist[ip]['reason'] = None
                self.save()
                return True
            return False

    def get_status(self):
        """
        获取黑名单状态信息

        Returns:
            dict: 统计信息
        """
        with self.lock:
            blocked_count = sum(1 for item in self.blacklist.values() if item.get('blocked', False))
            total_count = len(self.blacklist)

            return {
                'total_ips': total_count,
                'blocked_ips': blocked_count,
                'blacklist': dict(self.blacklist)
            }

    def get_blocked_ips(self):
        """
        获取所有被封锁的IP列表

        Returns:
            list: 被封锁的IP列表，每项包含IP和详细信息
        """
        with self.lock:
            blocked = []
            for ip, info in self.blacklist.items():
                if info.get('blocked', False):
                    blocked.append({
                        'ip': ip,
                        'fail_count': info.get('fail_count', 0),
                        'blocked_time': info.get('blocked_time'),
                        'reason': info.get('reason', '未知')
                    })
            return blocked

    def save(self):
        """保存黑名单到文件"""
        try:
            os.makedirs(os.path.dirname(self.blacklist_file), exist_ok=True)
            with open(self.blacklist_file, 'w', encoding='utf-8') as f:
                json.dump(self.blacklist, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"[错误] 保存IP黑名单失败: {e}")

    def load(self):
        """从文件加载黑名单"""
        try:
            if os.path.exists(self.blacklist_file):
                with open(self.blacklist_file, 'r', encoding='utf-8') as f:
                    self.blacklist = json.load(f)
                print(f"[FlashControler] 已加载IP黑名单，共 {len(self.blacklist)} 条记录")
            else:
                print("[FlashControler] IP黑名单文件不存在，使用空黑名单")
        except Exception as e:
            print(f"[错误] 加载IP黑名单失败: {e}")
            self.blacklist = {}
