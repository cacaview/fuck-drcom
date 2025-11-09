#!/usr/bin/env python3
"""
Dr.COM VPN 客户端启动脚本（命令行版 - 交互式）

⚠️ 免责声明：
本软件仅供学习和技术研究使用。使用本软件即表示您已阅读、理解并同意遵守完整的
《免责声明》（详见项目根目录下的"免责声明.md"文件）。

使用本软件产生的一切法律问题和后果由使用者自行承担，开发者不承担任何法律义务。
请严格遵守相关法律法规和学校网络使用规定。

发布日期：2025年11月7日
"""

import sys
sys.path.insert(0, '.')

from client.vpn_client import VPNClient
from common.config_manager import ConfigManager, interactive_input_client
from common.config import VPN_CONFIG
import signal

def main():
    """主函数"""
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
    
    print("=" * 60)
    print("💻 Dr.COM VPN 客户端（命令行版）")
    print("=" * 60)
    print()
    
    # 配置管理器
    config_manager = ConfigManager('client_config.encrypted')
    config = None
    
    # 检查是否存在已保存的配置
    if config_manager.config_exists():
        print("📁 检测到已保存的配置")
        choice = input("是否加载已保存的配置？(y/n) [y]: ").strip().lower()
        
        if choice != 'n':
            config = config_manager.load_config()
            if config is None:
                print("\n配置加载失败，将重新输入配置")
    
    # 如果没有配置或加载失败，交互式输入
    if config is None:
        config = interactive_input_client()
        
        # 询问是否保存配置
        print()
        save_choice = input("是否保存配置以便下次使用？(y/n) [y]: ").strip().lower()
        if save_choice != 'n':
            if config_manager.save_config(config):
                print("✓ 配置已加密保存，下次可直接加载")
            else:
                print("⚠️  配置保存失败，本次仍将继续运行")
    
    # 创建并启动客户端
    print("\n" + "=" * 60)
    username = config['username']
    password = config['password']
    server_ip = config['server_ip']
    server_port = config.get('port', VPN_CONFIG['server_port'])
    isp = config.get('isp', '中国电信')  # 默认中国电信
    connection_type = config.get('connection_type', 'auto')  # 默认自动检测
    
    client = VPNClient(username, password, server_ip, server_port, isp, connection_type=connection_type)
    
    # 注册信号处理
    def signal_handler(sig, frame):
        print("\n\n收到退出信号，正在断开连接...")
        client.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 启动客户端
    if client.start():
        print("\n客户端运行中，按 Ctrl+C 断开...")
    else:
        print("客户端启动失败！")
        sys.exit(1)

if __name__ == '__main__':
    main()

