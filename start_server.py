#!/usr/bin/env python3
"""
Dr.COM VPN 服务端启动脚本

⚠️ 免责声明：
此软件仅供学习用途使用，使用此软件则代表您愿意承担所造成的法律问题，
开发者不为此承担任何法律义务。
"""

import sys
sys.path.insert(0, '.')

from server.vpn_server import main

if __name__ == '__main__':
    print("=" * 60)
    print("⚠️  免责声明")
    print("=" * 60)
    print("此软件仅供学习用途使用。")
    print("使用此软件则代表您愿意承担所造成的法律问题，")
    print("开发者不为此承担任何法律义务。")
    print("=" * 60)
    print()
    main()

