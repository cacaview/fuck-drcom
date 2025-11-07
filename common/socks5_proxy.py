"""
SOCKS5 代理服务器实现
用于VPN服务器提供真实的流量转发功能
"""

import socket
import struct
import threading
import select
from .logger import Logger


class Socks5ProxyHandler:
    """SOCKS5代理处理器"""
    
    # SOCKS5协议常量
    SOCKS_VERSION = 5
    
    # 认证方法
    AUTH_NO_AUTH = 0
    AUTH_GSSAPI = 1
    AUTH_USERNAME_PASSWORD = 2
    AUTH_NO_ACCEPTABLE = 0xFF
    
    # 命令类型
    CMD_CONNECT = 1
    CMD_BIND = 2
    CMD_UDP_ASSOCIATE = 3
    
    # 地址类型
    ADDR_IPV4 = 1
    ADDR_DOMAIN = 3
    ADDR_IPV6 = 4
    
    # 响应状态
    REP_SUCCESS = 0
    REP_GENERAL_FAILURE = 1
    REP_CONNECTION_NOT_ALLOWED = 2
    REP_NETWORK_UNREACHABLE = 3
    REP_HOST_UNREACHABLE = 4
    REP_CONNECTION_REFUSED = 5
    REP_TTL_EXPIRED = 6
    REP_COMMAND_NOT_SUPPORTED = 7
    REP_ADDRESS_TYPE_NOT_SUPPORTED = 8
    
    def __init__(self, client_socket, client_id, logger=None):
        """
        初始化SOCKS5代理处理器
        
        Args:
            client_socket: 客户端socket
            client_id: 客户端ID
            logger: 日志记录器
        """
        self.client_socket = client_socket
        self.client_id = client_id
        self.logger = logger or Logger('Socks5ProxyHandler', 'socks5_proxy')
        self.remote_socket = None
        
    def handle(self):
        """
        处理SOCKS5代理请求
        
        Returns:
            bool: 是否成功处理
        """
        try:
            # 1. 握手阶段 - 协商认证方法
            if not self._handshake():
                return False
            
            # 2. 请求阶段 - 处理连接请求
            if not self._handle_request():
                return False
            
            # 3. 转发阶段 - 双向转发数据
            self._relay_data()
            
            return True
            
        except Exception as e:
            self.logger.error(f"[{self.client_id}] SOCKS5处理异常: {e}")
            return False
        finally:
            self._close_connections()
    
    def _handshake(self):
        """
        SOCKS5握手 - 协商认证方法
        
        Returns:
            bool: 握手是否成功
        """
        try:
            # 接收客户端握手请求
            # 格式: VER | NMETHODS | METHODS
            data = self.client_socket.recv(257)
            if len(data) < 2:
                self.logger.warning(f"[{self.client_id}] 握手数据不完整")
                return False
            
            version = data[0]
            nmethods = data[1]
            
            # 检查版本
            if version != self.SOCKS_VERSION:
                self.logger.warning(f"[{self.client_id}] 不支持的SOCKS版本: {version}")
                return False
            
            # 检查方法列表长度
            if len(data) < 2 + nmethods:
                self.logger.warning(f"[{self.client_id}] 方法列表不完整")
                return False
            
            methods = data[2:2+nmethods]
            
            # 选择认证方法（这里使用无认证）
            if self.AUTH_NO_AUTH in methods:
                # 发送选择的认证方法
                # 格式: VER | METHOD
                response = struct.pack('!BB', self.SOCKS_VERSION, self.AUTH_NO_AUTH)
                self.client_socket.send(response)
                self.logger.debug(f"[{self.client_id}] SOCKS5握手成功，使用无认证模式")
                return True
            else:
                # 没有可接受的认证方法
                response = struct.pack('!BB', self.SOCKS_VERSION, self.AUTH_NO_ACCEPTABLE)
                self.client_socket.send(response)
                self.logger.warning(f"[{self.client_id}] 没有可接受的认证方法")
                return False
                
        except Exception as e:
            self.logger.error(f"[{self.client_id}] 握手异常: {e}")
            return False
    
    def _handle_request(self):
        """
        处理SOCKS5请求
        
        Returns:
            bool: 请求是否成功处理
        """
        try:
            # 接收客户端请求
            # 格式: VER | CMD | RSV | ATYP | DST.ADDR | DST.PORT
            data = self.client_socket.recv(4)
            if len(data) < 4:
                self.logger.warning(f"[{self.client_id}] 请求数据不完整")
                self._send_reply(self.REP_GENERAL_FAILURE)
                return False
            
            version = data[0]
            cmd = data[1]
            # rsv = data[2]  # 保留字段
            atyp = data[3]
            
            # 检查版本
            if version != self.SOCKS_VERSION:
                self.logger.warning(f"[{self.client_id}] 不支持的SOCKS版本: {version}")
                self._send_reply(self.REP_GENERAL_FAILURE)
                return False
            
            # 目前只支持CONNECT命令
            if cmd != self.CMD_CONNECT:
                self.logger.warning(f"[{self.client_id}] 不支持的命令: {cmd}")
                self._send_reply(self.REP_COMMAND_NOT_SUPPORTED)
                return False
            
            # 解析目标地址
            dst_addr, dst_port = self._parse_address(atyp)
            if not dst_addr or not dst_port:
                self.logger.warning(f"[{self.client_id}] 无法解析目标地址")
                self._send_reply(self.REP_ADDRESS_TYPE_NOT_SUPPORTED)
                return False
            
            self.logger.info(f"[{self.client_id}] SOCKS5请求连接到: {dst_addr}:{dst_port}")
            
            # 连接到目标服务器
            if not self._connect_to_target(dst_addr, dst_port):
                return False
            
            # 发送成功响应
            self._send_reply(self.REP_SUCCESS, dst_addr, dst_port)
            self.logger.info(f"[{self.client_id}] 成功连接到目标服务器: {dst_addr}:{dst_port}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"[{self.client_id}] 处理请求异常: {e}")
            self._send_reply(self.REP_GENERAL_FAILURE)
            return False
    
    def _parse_address(self, atyp):
        """
        解析目标地址
        
        Args:
            atyp: 地址类型
            
        Returns:
            tuple: (地址, 端口)
        """
        try:
            if atyp == self.ADDR_IPV4:
                # IPv4地址: 4字节
                addr_data = self.client_socket.recv(4)
                addr = socket.inet_ntoa(addr_data)
            elif atyp == self.ADDR_DOMAIN:
                # 域名: 1字节长度 + 域名
                addr_len = ord(self.client_socket.recv(1))
                addr = self.client_socket.recv(addr_len).decode('utf-8')
            elif atyp == self.ADDR_IPV6:
                # IPv6地址: 16字节
                addr_data = self.client_socket.recv(16)
                addr = socket.inet_ntop(socket.AF_INET6, addr_data)
            else:
                self.logger.warning(f"[{self.client_id}] 不支持的地址类型: {atyp}")
                return None, None
            
            # 端口: 2字节
            port_data = self.client_socket.recv(2)
            port = struct.unpack('!H', port_data)[0]
            
            return addr, port
            
        except Exception as e:
            self.logger.error(f"[{self.client_id}] 解析地址异常: {e}")
            return None, None
    
    def _connect_to_target(self, addr, port):
        """
        连接到目标服务器
        
        Args:
            addr: 目标地址
            port: 目标端口
            
        Returns:
            bool: 连接是否成功
        """
        try:
            self.remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.remote_socket.settimeout(10)
            self.remote_socket.connect((addr, port))
            self.remote_socket.settimeout(None)
            return True
            
        except socket.timeout:
            self.logger.warning(f"[{self.client_id}] 连接目标超时: {addr}:{port}")
            self._send_reply(self.REP_TTL_EXPIRED)
            return False
        except ConnectionRefusedError:
            self.logger.warning(f"[{self.client_id}] 目标拒绝连接: {addr}:{port}")
            self._send_reply(self.REP_CONNECTION_REFUSED)
            return False
        except socket.gaierror:
            self.logger.warning(f"[{self.client_id}] 无法解析主机: {addr}")
            self._send_reply(self.REP_HOST_UNREACHABLE)
            return False
        except Exception as e:
            self.logger.error(f"[{self.client_id}] 连接目标异常: {e}")
            self._send_reply(self.REP_GENERAL_FAILURE)
            return False
    
    def _send_reply(self, reply, bind_addr='0.0.0.0', bind_port=0):
        """
        发送SOCKS5响应
        
        Args:
            reply: 响应代码
            bind_addr: 绑定地址（默认0.0.0.0）
            bind_port: 绑定端口（默认0）
        """
        try:
            # 格式: VER | REP | RSV | ATYP | BND.ADDR | BND.PORT
            response = struct.pack('!BBB', self.SOCKS_VERSION, reply, 0)
            
            # 添加绑定地址（使用IPv4）
            response += struct.pack('!B', self.ADDR_IPV4)
            response += socket.inet_aton(bind_addr)
            response += struct.pack('!H', bind_port)
            
            self.client_socket.send(response)
            
        except Exception as e:
            self.logger.error(f"[{self.client_id}] 发送响应异常: {e}")
    
    def _relay_data(self):
        """双向转发数据"""
        try:
            self.logger.info(f"[{self.client_id}] 开始转发数据")
            
            # 使用select实现双向数据转发
            sockets = [self.client_socket, self.remote_socket]
            
            while True:
                # 等待任一socket有数据可读
                readable, _, exceptional = select.select(sockets, [], sockets, 60)
                
                if exceptional:
                    self.logger.debug(f"[{self.client_id}] Socket异常，停止转发")
                    break
                
                if not readable:
                    # 超时，发送心跳检测
                    continue
                
                for sock in readable:
                    try:
                        # 从一个socket读取数据
                        data = sock.recv(8192)
                        
                        if not data:
                            # 连接关闭
                            self.logger.debug(f"[{self.client_id}] 连接关闭")
                            return
                        
                        # 转发到另一个socket
                        if sock is self.client_socket:
                            # 客户端 -> 远程服务器
                            self.remote_socket.sendall(data)
                            self.logger.debug(f"[{self.client_id}] 转发 {len(data)} 字节: 客户端->远程")
                        else:
                            # 远程服务器 -> 客户端
                            self.client_socket.sendall(data)
                            self.logger.debug(f"[{self.client_id}] 转发 {len(data)} 字节: 远程->客户端")
                    
                    except Exception as e:
                        self.logger.error(f"[{self.client_id}] 转发数据异常: {e}")
                        return
        
        except Exception as e:
            self.logger.error(f"[{self.client_id}] 数据转发异常: {e}")
    
    def _close_connections(self):
        """关闭所有连接"""
        if self.remote_socket:
            try:
                self.remote_socket.close()
            except:
                pass
        
        # 注意：不关闭client_socket，由调用方管理


class Socks5ProxyServer:
    """SOCKS5代理服务器（独立运行版）"""
    
    def __init__(self, host='0.0.0.0', port=1080):
        """
        初始化SOCKS5代理服务器
        
        Args:
            host: 监听地址
            port: 监听端口
        """
        self.host = host
        self.port = port
        self.logger = Logger('Socks5ProxyServer', 'socks5_proxy')
        self.server_socket = None
        self.running = False
        
    def start(self):
        """启动代理服务器"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            
            self.running = True
            self.logger.info(f"SOCKS5代理服务器启动: {self.host}:{self.port}")
            
            while self.running:
                client_socket, client_address = self.server_socket.accept()
                self.logger.info(f"接受连接: {client_address}")
                
                # 为每个客户端创建处理线程
                client_id = f"{client_address[0]}:{client_address[1]}"
                handler = Socks5ProxyHandler(client_socket, client_id, self.logger)
                
                thread = threading.Thread(target=handler.handle, daemon=True)
                thread.start()
        
        except Exception as e:
            self.logger.error(f"代理服务器异常: {e}")
        finally:
            self.stop()
    
    def stop(self):
        """停止代理服务器"""
        self.running = False
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        self.logger.info("SOCKS5代理服务器已停止")


# 用于测试的独立运行
if __name__ == '__main__':
    import sys
    
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 1080
    
    server = Socks5ProxyServer(port=port)
    
    try:
        server.start()
    except KeyboardInterrupt:
        print("\n正在关闭服务器...")
        server.stop()

