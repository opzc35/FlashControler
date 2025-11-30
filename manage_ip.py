#!/usr/bin/env python3
"""
IP黑名单管理工具
用于查看、解锁被封锁的IP地址
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from server.ip_blacklist import IPBlacklist


def print_help():
    """打印帮助信息"""
    print("=" * 60)
    print("FlashControler IP黑名单管理工具")
    print("=" * 60)
    print("\n使用方法:")
    print("  python manage_ip.py list          # 查看所有被封锁的IP")
    print("  python manage_ip.py status        # 查看黑名单状态")
    print("  python manage_ip.py unlock <IP>   # 解锁指定IP")
    print("  python manage_ip.py block <IP>    # 手动封锁IP")
    print("\n示例:")
    print("  python manage_ip.py list")
    print("  python manage_ip.py unlock 192.168.1.100")
    print("=" * 60)


def list_blocked_ips(blacklist):
    """列出所有被封锁的IP"""
    blocked_ips = blacklist.get_blocked_ips()

    if not blocked_ips:
        print("\n✓ 当前没有被封锁的IP")
        return

    print(f"\n{'=' * 80}")
    print(f"{'IP地址':<20} {'失败次数':<10} {'封锁时间':<20} {'封锁原因'}")
    print(f"{'=' * 80}")

    for item in blocked_ips:
        print(f"{item['ip']:<20} {item['fail_count']:<10} {item['blocked_time']:<20} {item['reason']}")

    print(f"{'=' * 80}")
    print(f"共 {len(blocked_ips)} 个IP被封锁\n")


def show_status(blacklist):
    """显示黑名单状态"""
    status = blacklist.get_status()

    print("\n" + "=" * 60)
    print("IP黑名单状态")
    print("=" * 60)
    print(f"总记录数: {status['total_ips']}")
    print(f"被封锁IP: {status['blocked_ips']}")
    print(f"自动封锁阈值: {blacklist.max_failures} 次认证失败")
    print("=" * 60 + "\n")


def unlock_ip(blacklist, ip):
    """解锁IP"""
    print(f"\n正在解锁 IP: {ip} ...")

    if blacklist.unblock_ip(ip):
        print(f"✓ 成功解锁 IP: {ip}")
    else:
        print(f"✗ IP {ip} 不在黑名单中或未被封锁")


def block_ip(blacklist, ip):
    """手动封锁IP"""
    print(f"\n正在封锁 IP: {ip} ...")

    # 检查是否已被封锁
    is_blocked, reason = blacklist.check_blocked(ip)
    if is_blocked:
        print(f"✗ IP {ip} 已经被封锁")
        print(f"   原因: {reason}")
        return

    blacklist.block_ip(ip, "管理员手动封锁")
    print(f"✓ 成功封锁 IP: {ip}")


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print_help()
        return

    command = sys.argv[1].lower()

    # 创建黑名单实例
    blacklist = IPBlacklist()

    if command == "help" or command == "-h" or command == "--help":
        print_help()

    elif command == "list":
        list_blocked_ips(blacklist)

    elif command == "status":
        show_status(blacklist)

    elif command == "unlock":
        if len(sys.argv) < 3:
            print("✗ 错误: 请指定要解锁的IP地址")
            print("   使用方法: python manage_ip.py unlock <IP>")
            return
        ip = sys.argv[2]
        unlock_ip(blacklist, ip)

    elif command == "block":
        if len(sys.argv) < 3:
            print("✗ 错误: 请指定要封锁的IP地址")
            print("   使用方法: python manage_ip.py block <IP>")
            return
        ip = sys.argv[2]
        block_ip(blacklist, ip)

    else:
        print(f"✗ 未知命令: {command}")
        print_help()


if __name__ == '__main__':
    main()
