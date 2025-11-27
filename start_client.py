#!/usr/bin/env python3
"""
Windows客户端启动脚本
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from client.client import main

if __name__ == '__main__':
    main()
