#!/usr/bin/env python3
"""
Dr.COM 校园网自动认证工具
适用于无图形界面的设备（服务器、路由器、嵌入式设备等）
"""

import sys
import time
import argparse
import logging
from pathlib import Path
from datetime import datetime

# 添加common目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from common.drcom_login import DrcomLogin

class DrcomAuth:
    """Dr.COM 认证工具主类"""
    
    def __init__(self, username=None, password=None, verbose=False, interface=None, ac_ip=None):
        """
        初始化认证工具
        
        Args:
            username: 用户名
            password: 密码
            verbose: 是否详细输出
            interface: 指定网络接口
            ac_ip: 指定AC IP地址
        """
        self.username = username
        self.password = password
        self.verbose = verbose
        self.interface = interface
        self.ac_ip = ac_ip
        
        # 设置日志
        log_level = logging.DEBUG if verbose else logging.INFO
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        self.logger = logging.getLogger(__name__)
        
        # 创建DrcomLogin实例
        self.drcom = DrcomLogin()
    
    def print_banner(self):
        """打印横幅"""
        print("=" * 60)
        print("Dr.COM 校园网自动认证工具")
        print("=" * 60)
    
    def login(self):
        """执行登录认证"""
        self.print_banner()
        
        # 获取用户名密码
        if not self.username:
            self.username = input("请输入用户名（学号）: ").strip()
        if not self.password:
            import getpass
            self.password = getpass.getpass("请输入密码: ").strip()
        
        if not self.username or not self.password:
            print("[ERROR] 用户名和密码不能为空")
            return False
        
        print(f"\n用户: {self.username}")
        print("正在认证...")
        print("-" * 60)
        
        try:
            # 执行登录
            result = self.drcom.login(self.username, self.password)
            
            print()
            if result.get('success'):
                print("[SUCCESS] 认证成功！")
                print("=" * 60)
                print(f"认证时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"设备IP: {result.get('ip', 'N/A')}")
                
                if result.get('message'):
                    print(f"消息: {result['message']}")
                
                print("=" * 60)
                return True
            else:
                print("[FAIL] 认证失败")
                if result.get('message'):
                    print(f"原因: {result['message']}")
                print("=" * 60)
                return False
                
        except Exception as e:
            print(f"[ERROR] 认证过程出错: {e}")
            if self.verbose:
                import traceback
                traceback.print_exc()
            return False
    
    def logout(self):
        """主动下线"""
        self.print_banner()
        print("正在下线...")
        print("-" * 60)
        
        try:
            result = self.drcom.logout()
            
            print()
            if result.get('success'):
                print("[SUCCESS] 下线成功")
            else:
                print("[FAIL] 下线失败")
                if result.get('message'):
                    print(f"原因: {result['message']}")
            print("=" * 60)
            return result.get('success', False)
            
        except Exception as e:
            print(f"[ERROR] 下线过程出错: {e}")
            if self.verbose:
                import traceback
                traceback.print_exc()
            return False
    
    def check_status(self):
        """查询在线状态"""
        self.print_banner()
        print("正在查询在线状态...")
        print("-" * 60)
        
        try:
            result = self.drcom.check_online_status()
            
            print()
            if result.get('online'):
                print("[ONLINE] 当前在线")
                print("=" * 60)
                if result.get('login_time'):
                    print(f"认证时间: {result['login_time']}")
                if result.get('online_duration'):
                    print(f"在线时长: {result['online_duration']}")
                if result.get('ip'):
                    print(f"设备IP: {result['ip']}")
                if result.get('mac'):
                    print(f"MAC地址: {result['mac']}")
                print("=" * 60)
            else:
                print("[OFFLINE] 当前离线")
                if result.get('message'):
                    print(f"提示: {result['message']}")
                print("=" * 60)
            
            return result.get('online', False)
            
        except Exception as e:
            print(f"[ERROR] 查询状态出错: {e}")
            if self.verbose:
                import traceback
                traceback.print_exc()
            return False
    
    def auto_reconnect(self, check_interval=60, max_retries=3):
        """
        自动重连模式
        
        Args:
            check_interval: 检查间隔（秒）
            max_retries: 最大重试次数
        """
        self.print_banner()
        print("启动自动重连模式")
        print(f"检查间隔: {check_interval}秒")
        print(f"最大重试: {max_retries}次")
        print("=" * 60)
        print("按 Ctrl+C 停止")
        print()
        
        consecutive_failures = 0
        
        try:
            while True:
                try:
                    # 检查在线状态
                    status = self.drcom.check_online_status()
                    
                    if status.get('online'):
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] 在线 - 状态正常")
                        consecutive_failures = 0
                    else:
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] 离线 - 尝试重连...")
                        
                        # 尝试重连
                        login_result = self.drcom.login(self.username, self.password)
                        
                        if login_result.get('success'):
                            print(f"[{datetime.now().strftime('%H:%M:%S')}] [SUCCESS] 重连成功")
                            consecutive_failures = 0
                        else:
                            consecutive_failures += 1
                            print(f"[{datetime.now().strftime('%H:%M:%S')}] [FAIL] 重连失败 ({consecutive_failures}/{max_retries})")
                            
                            if consecutive_failures >= max_retries:
                                print(f"[ERROR] 连续失败{max_retries}次，退出自动重连")
                                return False
                    
                    # 等待下一次检查
                    time.sleep(check_interval)
                    
                except KeyboardInterrupt:
                    raise
                except Exception as e:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] [ERROR] 检查失败: {e}")
                    consecutive_failures += 1
                    
                    if consecutive_failures >= max_retries:
                        print(f"[ERROR] 连续失败{max_retries}次，退出自动重连")
                        return False
                    
                    time.sleep(check_interval)
                    
        except KeyboardInterrupt:
            print("\n\n自动重连已停止")
            return True

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='Dr.COM 校园网自动认证工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
使用示例:
  # 一键认证
  python drcom_auth.py -u 学号 -p 密码
  
  # 查询状态
  python drcom_auth.py --status
  
  # 主动下线
  python drcom_auth.py --logout
  
  # 自动重连
  python drcom_auth.py -u 学号 -p 密码 --auto-reconnect
        '''
    )
    
    # 认证选项
    auth_group = parser.add_argument_group('认证选项')
    auth_group.add_argument('-u', '--username', help='用户名（学号）')
    auth_group.add_argument('-p', '--password', help='密码')
    
    # 操作选项
    action_group = parser.add_argument_group('操作选项')
    action_group.add_argument('--login', action='store_true', help='执行登录认证（默认）')
    action_group.add_argument('--logout', action='store_true', help='主动下线')
    action_group.add_argument('--status', action='store_true', help='查询在线状态')
    
    # 网络选项
    network_group = parser.add_argument_group('网络选项')
    network_group.add_argument('-i', '--interface', help='指定网络接口（如eth0, wlan0）')
    network_group.add_argument('--ac-ip', help='指定AC IP地址')
    
    # 行为选项
    behavior_group = parser.add_argument_group('行为选项')
    behavior_group.add_argument('--auto-reconnect', action='store_true', help='自动重连模式')
    behavior_group.add_argument('--check-interval', type=int, default=60, help='检查间隔（秒），默认60')
    behavior_group.add_argument('--max-retries', type=int, default=3, help='最大重试次数，默认3')
    
    # 输出选项
    output_group = parser.add_argument_group('输出选项')
    output_group.add_argument('-v', '--verbose', action='store_true', help='详细输出')
    output_group.add_argument('-q', '--quiet', action='store_true', help='静默模式')
    
    # 其他
    parser.add_argument('--version', action='version', version='Dr.COM Auth Tool v2.0.0')
    
    args = parser.parse_args()
    
    # 静默模式处理
    if args.quiet:
        logging.basicConfig(level=logging.ERROR)
    
    # 创建认证工具实例
    auth = DrcomAuth(
        username=args.username,
        password=args.password,
        verbose=args.verbose,
        interface=args.interface,
        ac_ip=args.ac_ip
    )
    
    # 执行操作
    try:
        if args.logout:
            # 主动下线
            success = auth.logout()
            sys.exit(0 if success else 1)
            
        elif args.status:
            # 查询状态
            online = auth.check_status()
            sys.exit(0 if online else 1)
            
        elif args.auto_reconnect:
            # 自动重连模式
            if not args.username or not args.password:
                print("[ERROR] 自动重连模式需要提供用户名和密码")
                print("使用: python drcom_auth.py -u 用户名 -p 密码 --auto-reconnect")
                sys.exit(1)
            
            success = auth.auto_reconnect(
                check_interval=args.check_interval,
                max_retries=args.max_retries
            )
            sys.exit(0 if success else 1)
            
        else:
            # 默认：执行登录
            success = auth.login()
            sys.exit(0 if success else 1)
            
    except KeyboardInterrupt:
        print("\n\n操作已取消")
        sys.exit(130)
    except Exception as e:
        print(f"\n[ERROR] 程序异常: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()

