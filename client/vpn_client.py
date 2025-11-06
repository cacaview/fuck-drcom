"""
VPN客户�?- 命令行版�?
"""

import socket
import time
import threading
import sys
from common.drcom_login import DrcomLogin
from common.config import VPN_CONFIG, RETRY_CONFIG
from common.logger import Logger


class VPNClient:
    """VPN客户�?""
    
    def __init__(self, username, password, server_ip, server_port=None):
        """
        初始化VPN客户�?
        
        Args:
            username: Dr.COM用户�?
            password: Dr.COM密码
            server_ip: 服务器IP地址
            server_port: 服务器端�?
        """
        self.username = username
        self.password = password
        self.server_ip = server_ip
        self.server_port = server_port or VPN_CONFIG['server_port']
        self.logger = Logger('VPNClient', 'vpn_client')
        
        self.login_manager = DrcomLogin(username, password)
        self.client_socket = None
        self.running = False
        self.local_ip = None
        
        # 心跳线程
        self.heartbeat_thread = None
        
    def start(self):
        """启动客户�?""
        self.logger.info("=" * 60)
        self.logger.info("VPN客户端启动中...")
        self.logger.info("=" * 60)
        
        # 第一步：登录网络
        self.logger.info("步骤1: 登录Dr.COM网络")
        login_result = self.login_manager.login_with_retry()
        
        if not login_result['success']:
            self.logger.critical(f"登录失败: {login_result['message']}")
            self.logger.critical("客户端启动失败！")
            return False
        
        self.local_ip = login_result['ip']
        self.logger.info(f"�?登录成功！客户端内网IP: {self.local_ip}")
        
        # 第二步：尝试连接服务�?
        self.logger.info(f"步骤2: 尝试连接服务�?{self.server_ip}:{self.server_port}")
        
        # 因为客户端登录后服务器会被踢下线，但仍可访问内网
        # 所以这里需要等待一下，让服务器重新登录
        max_connect_retries = 10
        connect_retry_delay = 5
        
        for attempt in range(1, max_connect_retries + 1):
            self.logger.info(f"�?{attempt}/{max_connect_retries} 次连接尝�?..")
            
            if self._connect_to_server():
                self.logger.info("�?成功连接到服务器�?)
                break
            
            if attempt < max_connect_retries:
                self.logger.warning(
                    f"连接失败，{connect_retry_delay}秒后重试..."
                )
                time.sleep(connect_retry_delay)
            else:
                self.logger.critical(
                    f"无法连接到服务器，已尝试{max_connect_retries}�?
                )
                return False
        
        # 第三步：向服务器报告客户端IP
        self.logger.info(f"步骤3: 向服务器报告客户端IP: {self.local_ip}")
        try:
            self.client_socket.send(f'REPORT_IP:{self.local_ip}'.encode('utf-8'))
            
            # 等待服务器重新登录的结果
            self.logger.info("等待服务器重新登录网�?..")
            response = self.client_socket.recv(1024).decode('utf-8')
            
            if response == 'LOGIN_SUCCESS':
                self.logger.info("�?服务器重新登录成功！")
            else:
                self.logger.error("服务器重新登录失败！")
                self.client_socket.close()
                return False
            
        except Exception as e:
            self.logger.error(f"与服务器通信失败: {e}")
            return False
        
        # 第四步：建立VPN连接
        self.logger.info("步骤4: 建立VPN连接")
        self.running = True
        
        # 启动心跳线程
        self.heartbeat_thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
        self.heartbeat_thread.start()
        
        self.logger.info("=" * 60)
        self.logger.info("�?VPN连接已建立！")
        self.logger.info(f"  客户端IP: {self.local_ip}")
        self.logger.info(f"  服务器IP: {self.server_ip}")
        self.logger.info(f"  现在可以通过服务器访问互联网")
        self.logger.info("=" * 60)
        
        # 保持连接
        self._maintain_connection()
        
        return True
    
    def _connect_to_server(self):
        """
        连接到服务器
        
        Returns:
            bool: 连接是否成功
        """
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.settimeout(10)
            
            self.logger.debug(f"正在连接 {self.server_ip}:{self.server_port}...")
            self.client_socket.connect((self.server_ip, self.server_port))
            
            # 发送握手信�?
            self.logger.debug("发送握手信�?..")
            hello_msg = f'HELLO:{self.local_ip}'
            self.client_socket.send(hello_msg.encode('utf-8'))
            
            # 等待服务器确�?
            response = self.client_socket.recv(1024)
            if response == b'OK':
                self.logger.debug("握手成功")
                return True
            else:
                self.logger.warning(f"握手失败: {response}")
                self.client_socket.close()
                return False
                
        except socket.timeout:
            self.logger.debug("连接超时")
            return False
        except ConnectionRefusedError:
            self.logger.debug("连接被拒绝（服务器可能未启动或被踢下线）")
            return False
        except Exception as e:
            self.logger.debug(f"连接异常: {e}")
            return False
    
    def _heartbeat_loop(self):
        """心跳循环"""
        self.logger.info("心跳线程已启�?)
        
        while self.running:
            try:
                time.sleep(VPN_CONFIG['heartbeat_interval'])
                
                # 发送心跳包
                self.client_socket.send(b'HEARTBEAT')
                
                # 接收响应（设置短超时�?
                self.client_socket.settimeout(5)
                response = self.client_socket.recv(1024)
                
                if response == b'HEARTBEAT_ACK':
                    self.logger.debug("心跳正常")
                else:
                    self.logger.warning(f"心跳响应异常: {response}")
                
            except socket.timeout:
                self.logger.warning("心跳超时")
            except Exception as e:
                self.logger.error(f"心跳异常: {e}")
                self.running = False
                break
    
    def _maintain_connection(self):
        """维持连接"""
        try:
            while self.running:
                time.sleep(1)
                
                # 可以在这里处理其他任�?
                # 例如：流量统计、网络测试等
                
        except KeyboardInterrupt:
            self.logger.info("收到退出信�?)
        finally:
            self.stop()
    
    def stop(self):
        """停止客户�?""
        self.logger.info("正在断开VPN连接...")
        self.running = False
        
        if self.client_socket:
            try:
                self.client_socket.close()
            except:
                pass
        
        self.logger.info("客户端已停止")


def main():
    """主函�?""
    import signal
    
    if len(sys.argv) < 4:
        print("=" * 60)
        print("Dr.COM VPN客户�?- 命令行版�?)
        print("=" * 60)
        print("用法: python vpn_client.py <用户�? <密码> <服务器IP> [服务器端口]")
        print("示例: python vpn_client.py MR646C80105795 mypassword 172.21.77.34 8888")
        print("=" * 60)
        sys.exit(1)
    
    username = sys.argv[1]
    password = sys.argv[2]
    server_ip = sys.argv[3]
    server_port = int(sys.argv[4]) if len(sys.argv) > 4 else VPN_CONFIG['server_port']
    
    # 创建客户端实�?
    client = VPNClient(username, password, server_ip, server_port)
    
    # 注册信号处理
    def signal_handler(sig, frame):
        print("\n收到退出信号，正在断开连接...")
        client.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 启动客户�?
    if client.start():
        print("客户端运行中，按 Ctrl+C 断开...")
    else:
        print("客户端启动失败！")
        sys.exit(1)


if __name__ == '__main__':
    main()

