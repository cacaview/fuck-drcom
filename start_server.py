#!/usr/bin/env python3
"""
Dr.COM VPN 服务端启动脚本（交互式）

⚠️ 免责声明：
此软件仅供学习用途使用，使用此软件则代表您愿意承担所造成的法律问题，
开发者不为此承担任何法律义务。
"""

import sys
sys.path.insert(0, '.')

from server.vpn_server import VPNServer
from common.config_manager import ConfigManager, interactive_input_server
from common.config import VPN_CONFIG
import signal

def main():
    """主函数"""
    print("=" * 60)
    print("⚠️  免责声明")
    print("=" * 60)
    print("此软件仅供学习用途使用。")
    print("使用此软件则代表您愿意承担所造成的法律问题，")
    print("开发者不为此承担任何法律义务。")
    print("=" * 60)
    print()
    
    print("=" * 60)
    print("🚀 Dr.COM VPN 服务端")
    print("=" * 60)
    print()
    
    # 配置管理器
    config_manager = ConfigManager('server_config.encrypted')
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
        config = interactive_input_server()
        
        # 询问是否保存配置
        print()
        save_choice = input("是否保存配置以便下次使用？(y/n) [y]: ").strip().lower()
        if save_choice != 'n':
            if config_manager.save_config(config):
                print("✓ 配置已加密保存，下次可直接加载")
            else:
                print("⚠️  配置保存失败，本次仍将继续运行")
    
    # 创建并启动服务器
    print("\n" + "=" * 60)
    username = config['username']
    password = config['password']
    port = config.get('port', VPN_CONFIG['server_port'])
    
    server = VPNServer(username, password, port)
    
    # 注册信号处理
    def signal_handler(sig, frame):
        print("\n\n收到退出信号，正在关闭服务器...")
        server.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 启动服务器
    if server.start():
        print("\n服务器运行中，按 Ctrl+C 停止...")
        # 保持主线程运行
        try:
            import time
            while server.running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n正在关闭服务器...")
            server.stop()
    else:
        print("服务器启动失败！")
        sys.exit(1)

if __name__ == '__main__':
    main()

