"""
VPN服务�?- 提供网络共享服务
"""

import socket
import threading
import time
import struct
from common.drcom_login import DrcomLogin
from common.config import VPN_CONFIG, RETRY_CONFIG
from common.logger import Logger


class VPNServer:
    """VPN服务�?""
    
    def __init__(self, username, password, port=None):
        """
        初始化VPN服务�?
        
        Args:
            username: Dr.COM用户�?
            password: Dr.COM密码
            port: 监听端口
        """
        self.username = username
        self.password = password
        self.port = port or VPN_CONFIG['server_port']
        self.logger = Logger('VPNServer', 'vpn_server')
        
        self.login_manager = DrcomLogin(username, password)
        self.server_socket = None
        self.running = False
        self.clients = {}  # {client_id: client_info}
        self.local_ip = None
        
        # 心跳线程
        self.heartbeat_thread = None
        
    def start(self):
        """启动服务�?""
        self.logger.info("=" * 60)
        self.logger.info("VPN服务器启动中...")
        self.logger.info("=" * 60)
        
        # 第一步：登录网络
        self.logger.info("步骤1: 登录Dr.COM网络")
        login_result = self.login_manager.login_with_retry()
        
        if not login_result['success']:
            self.logger.critical(f"登录失败: {login_result['message']}")
            self.logger.critical("服务器启动失败！")
            return False
        
        self.local_ip = login_result['ip']
        self.logger.info(f"�?登录成功！服务器内网IP: {self.local_ip}")
        
        # 第二步：启动监听服务
        self.logger.info(f"步骤2: 启动VPN服务，监听端�?{self.port}")
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind(('0.0.0.0', self.port))
            self.server_socket.listen(5)
            
            self.running = True
            self.logger.info(f"�?VPN服务已启动，监听 0.0.0.0:{self.port}")
            self.logger.info("=" * 60)
            self.logger.info(f"服务器信�?")
            self.logger.info(f"  内网IP: {self.local_ip}")
            self.logger.info(f"  监听端口: {self.port}")
            self.logger.info(f"  请在客户端使用以下信息连�?")
            self.logger.info(f"    服务器IP: {self.local_ip}")
            self.logger.info(f"    端口: {self.port}")
            self.logger.info("=" * 60)
            
            # 启动心跳监控线程
            self.heartbeat_thread = threading.Thread(target=self._heartbeat_monitor, daemon=True)
            self.heartbeat_thread.start()
            
            # 开始接受客户端连接
            self._accept_clients()
            
        except Exception as e:
            self.logger.critical(f"启动VPN服务失败: {e}")
            return False
        
        return True
    
    def _accept_clients(self):
        """接受客户端连�?""
        self.logger.info("开始接受客户端连接...")
        
        while self.running:
            try:
                client_socket, client_address = self.server_socket.accept()
                self.logger.info(f"收到来自 {client_address} 的连接请�?)
                
                # 为每个客户端创建处理线程
                client_thread = threading.Thread(
                    target=self._handle_client,
                    args=(client_socket, client_address),
                    daemon=True
                )
                client_thread.start()
                
            except Exception as e:
                if self.running:
                    self.logger.error(f"接受客户端连接时出错: {e}")
    
    def _handle_client(self, client_socket, client_address):
        """
        处理客户端连�?
        
        Args:
            client_socket: 客户端socket
            client_address: 客户端地址
        """
        client_id = f"{client_address[0]}:{client_address[1]}"
        
        try:
            # 接收客户端握手信�?
            self.logger.info(f"[{client_id}] 等待客户端握�?..")
            data = client_socket.recv(1024).decode('utf-8')
            
            if not data.startswith('HELLO:'):
                self.logger.warning(f"[{client_id}] 收到无效握手: {data}")
                client_socket.close()
                return
            
            # 解析客户端IP
            client_ip = data.split(':', 1)[1].strip()
            self.logger.info(f"[{client_id}] 客户端握手成功，客户端IP: {client_ip}")
            
            # 保存客户端信�?
            self.clients[client_id] = {
                'socket': client_socket,
                'address': client_address,
                'ip': client_ip,
                'connected_time': time.time(),
                'last_heartbeat': time.time()
            }
            
            # 发送确�?
            client_socket.send(b'OK')
            
            # 提示：客户端连接后，服务器需要重新登录（会被客户端踢下线�?
            self.logger.warning(f"[{client_id}] 客户端连接成功！")
            self.logger.warning(f"[{client_id}] 注意: 客户端可能正在登录，服务器将被踢下线...")
            self.logger.info(f"[{client_id}] 等待客户端报告其IP并尝试重新登�?..")
            
            # 等待客户端发送IP报告
            report_data = client_socket.recv(1024).decode('utf-8')
            if report_data.startswith('REPORT_IP:'):
                reported_ip = report_data.split(':', 1)[1].strip()
                self.logger.info(f"[{client_id}] 收到客户端IP报告: {reported_ip}")
                
                # 尝试重新登录（抢回网络）
                self.logger.info(f"[{client_id}] 开始重新登录网�?..")
                login_result = self.login_manager.login_with_retry()
                
                if login_result['success']:
                    self.logger.info(f"[{client_id}] �?重新登录成功�?)
                    client_socket.send(b'LOGIN_SUCCESS')
                    
                    # 开始提供VPN服务
                    self._provide_vpn_service(client_socket, client_id)
                else:
                    self.logger.error(f"[{client_id}] 重新登录失败: {login_result['message']}")
                    client_socket.send(b'LOGIN_FAILED')
                    client_socket.close()
                    del self.clients[client_id]
            
        except Exception as e:
            self.logger.error(f"[{client_id}] 处理客户端时出错: {e}")
            if client_id in self.clients:
                del self.clients[client_id]
            try:
                client_socket.close()
            except:
                pass
    
    def _provide_vpn_service(self, client_socket, client_id):
        """
        为客户端提供VPN服务（简单的SOCKS5代理�?
        
        Args:
            client_socket: 客户端socket
            client_id: 客户端ID
        """
        self.logger.info(f"[{client_id}] 开始提供VPN服务")
        
        try:
            while self.running:
                # 接收客户端请�?
                data = client_socket.recv(VPN_CONFIG['buffer_size'])
                
                if not data:
                    self.logger.info(f"[{client_id}] 客户端断开连接")
                    break
                
                # 更新心跳时间
                if client_id in self.clients:
                    self.clients[client_id]['last_heartbeat'] = time.time()
                
                # 处理心跳�?
                if data == b'HEARTBEAT':
                    client_socket.send(b'HEARTBEAT_ACK')
                    continue
                
                # 处理代理请求
                # 这里实现简单的流量转发
                self.logger.debug(f"[{client_id}] 收到数据: {len(data)} 字节")
                
                # TODO: 实现完整的代理逻辑
                # 目前只是简单的回显
                client_socket.send(b'OK')
                
        except Exception as e:
            self.logger.error(f"[{client_id}] VPN服务出错: {e}")
        finally:
            if client_id in self.clients:
                del self.clients[client_id]
            try:
                client_socket.close()
            except:
                pass
            self.logger.info(f"[{client_id}] 连接已关�?)
    
    def _heartbeat_monitor(self):
        """心跳监控线程"""
        self.logger.info("心跳监控线程已启�?)
        
        while self.running:
            try:
                time.sleep(VPN_CONFIG['heartbeat_interval'])
                
                # 检查所有客户端的心�?
                current_time = time.time()
                timeout_clients = []
                
                for client_id, client_info in self.clients.items():
                    last_heartbeat = client_info['last_heartbeat']
                    if current_time - last_heartbeat > VPN_CONFIG['heartbeat_interval'] * 2:
                        timeout_clients.append(client_id)
                
                # 清理超时客户�?
                for client_id in timeout_clients:
                    self.logger.warning(f"[{client_id}] 心跳超时，断开连接")
                    try:
                        self.clients[client_id]['socket'].close()
                    except:
                        pass
                    del self.clients[client_id]
                
                # 显示当前连接状�?
                if self.clients:
                    self.logger.debug(f"当前连接�? {len(self.clients)}")
                
            except Exception as e:
                self.logger.error(f"心跳监控出错: {e}")
    
    def stop(self):
        """停止服务�?""
        self.logger.info("正在停止服务�?..")
        self.running = False
        
        # 关闭所有客户端连接
        for client_id, client_info in list(self.clients.items()):
            try:
                client_info['socket'].close()
            except:
                pass
        
        self.clients.clear()
        
        # 关闭服务器socket
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        
        self.logger.info("服务器已停止")


def main():
    """主函�?""
    import sys
    import signal
    
    if len(sys.argv) < 3:
        print("=" * 60)
        print("Dr.COM VPN服务�?)
        print("=" * 60)
        print("用法: python vpn_server.py <用户�? <密码> [端口]")
        print("示例: python vpn_server.py MR646C80105795 mypassword 8888")
        print("=" * 60)
        sys.exit(1)
    
    username = sys.argv[1]
    password = sys.argv[2]
    port = int(sys.argv[3]) if len(sys.argv) > 3 else VPN_CONFIG['server_port']
    
    # 创建服务器实�?
    server = VPNServer(username, password, port)
    
    # 注册信号处理
    def signal_handler(sig, frame):
        print("\n收到退出信号，正在关闭服务�?..")
        server.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 启动服务�?
    if server.start():
        print("服务器运行中，按 Ctrl+C 停止...")
        # 保持主线程运�?
        try:
            while server.running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n正在关闭服务�?..")
            server.stop()
    else:
        print("服务器启动失败！")
        sys.exit(1)


if __name__ == '__main__':
    main()

