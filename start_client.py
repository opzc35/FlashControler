#!/usr/bin/env python3
"""
FlashControler 客户端启动脚本
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from client.client_pyqt5 import main
except ImportError as e:
    print("错误: 无法启动客户端")
    print(f"原因: {e}")
    print("\n请安装PyQt5依赖:")
    print("  pip install PyQt5")
    sys.exit(1)

if __name__ == '__main__':
    main()
