"""
VPN客户端 - 命令行版本
提供本地SOCKS5代理，将流量转发到VPN服务器
"""

import socket
import time
import threading
import sys
import select
from common.drcom_login import DrcomLogin
from common.config import VPN_CONFIG, RETRY_CONFIG
from common.logger import Logger


class VPNClient:
    """VPN客户端"""
    
    def __init__(self, username, password, server_ip, server_port=None, isp='中国电信', local_proxy_port=1080, connection_type='auto'):
        """
        初始化VPN客户端
        
        Args:
            username: Dr.COM用户名
            password: Dr.COM密码
            server_ip: 服务器IP地址
            server_port: 服务器端口
            isp: 运营商类型，如'中国电信'、'中国联通'等
            local_proxy_port: 本地SOCKS5代理端口
            connection_type: 连接方式（auto/wifi/wired）
        """
        self.username = username
        self.password = password
        self.server_ip = server_ip
        self.server_port = server_port or VPN_CONFIG['server_port']
        self.isp = isp
        self.local_proxy_port = local_proxy_port
        self.connection_type = connection_type
        self.logger = Logger('VPNClient', 'vpn_client')
        
        self.login_manager = DrcomLogin(username, password, isp, connection_type)
        self.server_connection = None  # 到VPN服务器的主连接
        self.running = False
        self.local_ip = None
        
        # 本地SOCKS5代理服务器
        self.local_proxy_socket = None
        self.local_proxy_thread = None
        
    def start(self):
        """启动客户端"""
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
        self.logger.info(f"✓ 登录成功！客户端内网IP: {self.local_ip}")
        
        # 第二步：尝试连接服务器
        self.logger.info(f"步骤2: 尝试连接服务器 {self.server_ip}:{self.server_port}")
        
        # 因为客户端登录后服务器会被踢下线，但仍可访问内网
        # 所以这里需要等待一下，让服务器重新登录
        max_connect_retries = 10
        connect_retry_delay = 5
        
        for attempt in range(1, max_connect_retries + 1):
            self.logger.info(f"第 {attempt}/{max_connect_retries} 次连接尝试...")
            
            if self._connect_to_server():
                self.logger.info("✓ 成功连接到服务器！")
                break
            
            if attempt < max_connect_retries:
                self.logger.warning(
                    f"连接失败，{connect_retry_delay}秒后重试..."
                )
                time.sleep(connect_retry_delay)
            else:
                self.logger.critical(
                    f"无法连接到服务器，已尝试{max_connect_retries}次"
                )
                return False
        
        # 第三步：向服务器报告客户端IP
        self.logger.info(f"步骤3: 向服务器报告客户端IP: {self.local_ip}")
        try:
            self.server_connection.send(f'REPORT_IP:{self.local_ip}'.encode('utf-8'))
            
            # 等待服务器重新登录的结果
            self.logger.info("等待服务器重新登录网络...")
            self.server_connection.settimeout(60)  # 给服务器足够的时间重新登录
            response = self.server_connection.recv(1024).decode('utf-8')
            self.server_connection.settimeout(None)
            
            if response == 'LOGIN_SUCCESS':
                self.logger.info("✓ 服务器重新登录成功！")
            else:
                self.logger.error("服务器重新登录失败！")
                self.server_connection.close()
                return False
            
        except Exception as e:
            self.logger.error(f"与服务器通信失败: {e}")
            return False
        
        # 第四步：启动本地SOCKS5代理服务
        self.logger.info(f"步骤4: 启动本地SOCKS5代理服务")
        if not self._start_local_proxy():
            self.logger.error("启动本地代理服务失败！")
            return False
        
        self.running = True
        
        self.logger.info("=" * 60)
        self.logger.info("✓ VPN连接已建立！")
        self.logger.info(f"  客户端IP: {self.local_ip}")
        self.logger.info(f"  服务器IP: {self.server_ip}")
        self.logger.info(f"  本地SOCKS5代理: 127.0.0.1:{self.local_proxy_port}")
        self.logger.info("")
        self.logger.info("使用方法：")
        self.logger.info(f"  1. 配置应用程序使用SOCKS5代理: 127.0.0.1:{self.local_proxy_port}")
        self.logger.info(f"  2. 或者使用curl测试: curl --socks5 127.0.0.1:{self.local_proxy_port} http://www.bing.com")
        self.logger.info("=" * 60)
        
        # 保持运行
        self._maintain_connection()
        
        return True
    
    def _connect_to_server(self):
        """
        连接到服务器
        
        Returns:
            bool: 连接是否成功
        """
        try:
            self.server_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_connection.settimeout(10)
            
            self.logger.debug(f"正在连接 {self.server_ip}:{self.server_port}...")
            self.server_connection.connect((self.server_ip, self.server_port))
            
            # 发送握手信息
            self.logger.debug("发送握手信息...")
            hello_msg = f'HELLO:{self.local_ip}'
            self.server_connection.send(hello_msg.encode('utf-8'))
            
            # 等待服务器确认
            response = self.server_connection.recv(1024)
            if response == b'OK':
                self.logger.debug("握手成功")
                return True
            else:
                self.logger.warning(f"握手失败: {response}")
                self.server_connection.close()
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
    
    def _start_local_proxy(self):
        """
        启动本地SOCKS5代理服务器
        
        Returns:
            bool: 是否启动成功
        """
        try:
            self.local_proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.local_proxy_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.local_proxy_socket.bind(('127.0.0.1', self.local_proxy_port))
            self.local_proxy_socket.listen(5)
            
            # 启动代理服务线程
            self.local_proxy_thread = threading.Thread(
                target=self._accept_local_connections,
                daemon=True
            )
            self.local_proxy_thread.start()
            
            self.logger.info(f"✓ 本地SOCKS5代理已启动: 127.0.0.1:{self.local_proxy_port}")
            return True
            
        except Exception as e:
            self.logger.error(f"启动本地代理失败: {e}")
            return False
    
    def _accept_local_connections(self):
        """接受本地应用程序的连接"""
        self.logger.info("开始接受本地应用连接...")
        
        while self.running:
            try:
                client_socket, client_address = self.local_proxy_socket.accept()
                self.logger.debug(f"接受本地连接: {client_address}")
                
                # 为每个连接创建转发线程
                forward_thread = threading.Thread(
                    target=self._forward_to_server,
                    args=(client_socket, client_address),
                    daemon=True
                )
                forward_thread.start()
                
            except Exception as e:
                if self.running:
                    self.logger.error(f"接受本地连接时出错: {e}")
    
    def _forward_to_server(self, client_socket, client_address):
        """
        将本地应用的SOCKS5请求转发到VPN服务器
        
        Args:
            client_socket: 本地应用的socket
            client_address: 本地应用的地址
        """
        client_id = f"Local-{client_address[0]}:{client_address[1]}"
        remote_socket = None
        
        try:
            # 创建到VPN服务器的新连接
            remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            remote_socket.connect((self.server_ip, self.server_port))
            
            # 发送简化的握手（服务器已知客户端）
            hello_msg = f'HELLO:{self.local_ip}'
            remote_socket.send(hello_msg.encode('utf-8'))
            response = remote_socket.recv(1024)
            
            if response != b'OK':
                self.logger.warning(f"[{client_id}] 连接服务器失败")
                client_socket.close()
                return
            
            # 发送IP报告
            remote_socket.send(f'REPORT_IP:{self.local_ip}'.encode('utf-8'))
            response = remote_socket.recv(1024)
            
            if response != b'LOGIN_SUCCESS':
                self.logger.warning(f"[{client_id}] 服务器未就绪")
                client_socket.close()
                return
            
            self.logger.debug(f"[{client_id}] 开始转发SOCKS5流量")
            
            # 双向转发数据
            self._relay_data(client_socket, remote_socket, client_id)
            
        except Exception as e:
            self.logger.error(f"[{client_id}] 转发异常: {e}")
        finally:
            if remote_socket:
                try:
                    remote_socket.close()
                except:
                    pass
            try:
                client_socket.close()
            except:
                pass
            self.logger.debug(f"[{client_id}] 连接已关闭")
    
    def _relay_data(self, local_socket, remote_socket, client_id):
        """
        双向转发数据
        
        Args:
            local_socket: 本地socket
            remote_socket: 远程socket
            client_id: 客户端ID
        """
        try:
            sockets = [local_socket, remote_socket]
            
            while self.running:
                readable, _, exceptional = select.select(sockets, [], sockets, 60)
                
                if exceptional:
                    break
                
                if not readable:
                    continue
                
                for sock in readable:
                    try:
                        data = sock.recv(8192)
                        
                        if not data:
                            return
                        
                        if sock is local_socket:
                            # 本地应用 -> VPN服务器
                            remote_socket.sendall(data)
                            self.logger.debug(f"[{client_id}] → {len(data)}字节")
                        else:
                            # VPN服务器 -> 本地应用
                            local_socket.sendall(data)
                            self.logger.debug(f"[{client_id}] ← {len(data)}字节")
                    
                    except Exception as e:
                        self.logger.error(f"[{client_id}] 转发数据异常: {e}")
                        return
        
        except Exception as e:
            self.logger.error(f"[{client_id}] 数据转发异常: {e}")
    
    def _maintain_connection(self):
        """维持连接"""
        try:
            while self.running:
                time.sleep(1)
                
        except KeyboardInterrupt:
            self.logger.info("收到退出信号")
        finally:
            self.stop()
    
    def stop(self):
        """停止客户端"""
        self.logger.info("正在断开VPN连接...")
        self.running = False
        
        # 关闭本地代理服务器
        if self.local_proxy_socket:
            try:
                self.local_proxy_socket.close()
            except:
                pass
        
        # 关闭到VPN服务器的连接
        if self.server_connection:
            try:
                self.server_connection.close()
            except:
                pass
        
        self.logger.info("客户端已停止")


def main():
    """主函数"""
    import signal
    
    if len(sys.argv) < 4:
        print("=" * 60)
        print("Dr.COM VPN客户端 - 命令行版本")
        print("=" * 60)
        print("用法: python vpn_client.py <用户名> <密码> <服务器IP> [服务器端口] [本地代理端口]")
        print("示例: python vpn_client.py MR646C80105795 mypassword 172.21.77.34 8888 1080")
        print("=" * 60)
        sys.exit(1)
    
    username = sys.argv[1]
    password = sys.argv[2]
    server_ip = sys.argv[3]
    server_port = int(sys.argv[4]) if len(sys.argv) > 4 else VPN_CONFIG['server_port']
    local_proxy_port = int(sys.argv[5]) if len(sys.argv) > 5 else 1080
    
    # 创建客户端实例
    client = VPNClient(username, password, server_ip, server_port, local_proxy_port)
    
    # 注册信号处理
    def signal_handler(sig, frame):
        print("\n收到退出信号，正在断开连接...")
        client.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 启动客户端
    if client.start():
        print("客户端运行中，按 Ctrl+C 断开...")
    else:
        print("客户端启动失败！")
        sys.exit(1)


if __name__ == '__main__':
    main()
