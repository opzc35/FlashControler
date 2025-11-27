#!/usr/bin/env python3
"""
Windows客户端启动脚本 (PyQt5美化版本)
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 检查PyQt5是否安装
try:
    import PyQt5
    from client.client_pyqt5 import main
    print("使用PyQt5美化界面...")
except ImportError:
    print("PyQt5未安装，使用tkinter界面...")
    print("提示：安装PyQt5以获得更好的界面体验: pip install PyQt5")
    from client.client import main

if __name__ == '__main__':
    main()
