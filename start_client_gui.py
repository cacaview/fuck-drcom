#!/usr/bin/env python3
"""
Dr.COM VPN 客户端启动脚本（GUI版）

⚠️ 免责声明：
本软件仅供学习和技术研究使用。使用本软件即表示您已阅读、理解并同意遵守完整的
《免责声明》（详见项目根目录下的"免责声明.md"文件）。

使用本软件产生的一切法律问题和后果由使用者自行承担，开发者不承担任何法律义务。
请严格遵守相关法律法规和学校网络使用规定。

发布日期：2025年11月7日
"""

import sys
sys.path.insert(0, '.')

import flet as ft

print("=" * 70)
print("⚠️  免责声明")
print("=" * 70)
print("本软件仅供学习和技术研究使用。")
print("使用本软件即表示您已阅读、理解并同意遵守完整的《免责声明》。")
print('详见项目根目录下的"免责声明.md"文件。')
print()
print("使用本软件产生的一切法律问题和后果由使用者自行承担，")
print("开发者不承担任何法律义务。")
print("请严格遵守相关法律法规和学校网络使用规定。")
print()
print("发布日期：2025年11月7日")
print("=" * 70)
print()

from client_gui.vpn_client_gui import main

if __name__ == '__main__':
    # GUI版本保持原样，在GUI界面中处理配置保存
    ft.app(target=main)

