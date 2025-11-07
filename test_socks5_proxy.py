#!/usr/bin/env python3
"""
SOCKS5代理测试脚本
用于验证VPN系统的代理功能是否正常工作
"""

import socket
import struct
import sys


def test_socks5_connection(proxy_host='127.0.0.1', proxy_port=1080, 
                          target_host='www.bing.com', target_port=80):
    """
    测试SOCKS5代理连接
    
    Args:
        proxy_host: 代理服务器地址
        proxy_port: 代理服务器端口
        target_host: 目标主机
        target_port: 目标端口
    
    Returns:
        bool: 测试是否成功
    """
    print("=" * 60)
    print("SOCKS5 代理测试")
    print("=" * 60)
    print(f"代理服务器: {proxy_host}:{proxy_port}")
    print(f"目标服务器: {target_host}:{target_port}")
    print()
    
    try:
        # 1. 连接到代理服务器
        print("步骤1: 连接到代理服务器...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        sock.connect((proxy_host, proxy_port))
        print("✓ 连接成功")
        
        # 2. SOCKS5握手 - 发送认证方法
        print("\n步骤2: SOCKS5握手...")
        # VER | NMETHODS | METHODS
        # 0x05 | 0x01 | 0x00 (无认证)
        sock.send(b'\x05\x01\x00')
        
        # 接收服务器选择的认证方法
        response = sock.recv(2)
        if len(response) != 2 or response[0] != 0x05:
            print("✗ 握手失败: 无效响应")
            return False
        
        if response[1] != 0x00:
            print(f"✗ 握手失败: 不支持的认证方法 {response[1]}")
            return False
        
        print("✓ 握手成功（无认证模式）")
        
        # 3. 发送连接请求
        print("\n步骤3: 发送CONNECT请求...")
        # VER | CMD | RSV | ATYP | DST.ADDR | DST.PORT
        # 0x05 | 0x01 | 0x00 | 0x03 (域名) | domain_len | domain | port
        
        request = bytearray()
        request.append(0x05)  # SOCKS版本
        request.append(0x01)  # CMD: CONNECT
        request.append(0x00)  # RSV: 保留
        request.append(0x03)  # ATYP: 域名
        
        # 添加域名
        domain_bytes = target_host.encode('utf-8')
        request.append(len(domain_bytes))
        request.extend(domain_bytes)
        
        # 添加端口
        request.extend(struct.pack('!H', target_port))
        
        sock.send(bytes(request))
        print(f"✓ 已发送CONNECT请求: {target_host}:{target_port}")
        
        # 4. 接收连接响应
        print("\n步骤4: 等待服务器响应...")
        response = sock.recv(10)
        
        if len(response) < 4:
            print("✗ 响应不完整")
            return False
        
        if response[0] != 0x05:
            print(f"✗ 无效的SOCKS版本: {response[0]}")
            return False
        
        reply_code = response[1]
        if reply_code != 0x00:
            error_messages = {
                0x01: "一般SOCKS服务器失败",
                0x02: "连接不被允许",
                0x03: "网络不可达",
                0x04: "主机不可达",
                0x05: "连接被拒绝",
                0x06: "TTL过期",
                0x07: "不支持的命令",
                0x08: "不支持的地址类型"
            }
            error_msg = error_messages.get(reply_code, f"未知错误 ({reply_code})")
            print(f"✗ 连接失败: {error_msg}")
            return False
        
        print("✓ CONNECT成功！已建立到目标服务器的连接")
        
        # 5. 发送HTTP请求测试实际通信
        print("\n步骤5: 测试HTTP通信...")
        http_request = f"GET / HTTP/1.1\r\nHost: {target_host}\r\nConnection: close\r\n\r\n"
        sock.send(http_request.encode('utf-8'))
        print("✓ 已发送HTTP GET请求")
        
        # 接收响应
        print("\n步骤6: 接收HTTP响应...")
        response = sock.recv(4096).decode('utf-8', errors='ignore')
        
        if 'HTTP/' in response:
            print("✓ 收到HTTP响应！")
            lines = response.split('\r\n')
            status_line = lines[0]
            print(f"\n响应状态: {status_line}")
            print(f"响应大小: {len(response)} 字节")
            print("\n前200个字符:")
            print("-" * 60)
            print(response[:200])
            print("-" * 60)
            return True
        else:
            print("✗ 未收到有效的HTTP响应")
            print(f"收到的数据: {response[:100]}")
            return False
        
    except socket.timeout:
        print("✗ 连接超时")
        return False
    except ConnectionRefusedError:
        print("✗ 连接被拒绝（代理服务器可能未启动）")
        return False
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        try:
            sock.close()
        except:
            pass


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("VPN系统 - SOCKS5代理功能测试")
    print("=" * 60)
    print()
    print("此脚本将测试本地SOCKS5代理是否正常工作")
    print("请确保VPN客户端已经启动并连接到服务器")
    print()
    
    # 使用默认参数测试
    proxy_host = '127.0.0.1'
    proxy_port = 1080
    
    # 允许命令行参数
    if len(sys.argv) > 1:
        proxy_host = sys.argv[1]
    if len(sys.argv) > 2:
        proxy_port = int(sys.argv[2])
    
    print(f"测试配置:")
    print(f"  代理地址: {proxy_host}:{proxy_port}")
    print()
    
    # 测试1: HTTP连接
    print("\n" + "=" * 60)
    print("测试1: HTTP连接到 www.bing.com")
    print("=" * 60)
    success1 = test_socks5_connection(proxy_host, proxy_port, 'www.bing.com', 80)
    
    print("\n\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    if success1:
        print("✓ 所有测试通过！SOCKS5代理工作正常")
        print("\n你现在可以:")
        print(f"  1. 配置浏览器使用 SOCKS5 代理: {proxy_host}:{proxy_port}")
        print(f"  2. 使用curl测试: curl --socks5 {proxy_host}:{proxy_port} http://www.bing.com")
        print("  3. 配置其他应用程序使用此代理")
        return 0
    else:
        print("✗ 测试失败")
        print("\n可能的原因:")
        print("  1. VPN客户端未启动")
        print("  2. 代理端口不正确")
        print("  3. VPN服务器未连接")
        print("  4. 网络连接问题")
        return 1


if __name__ == '__main__':
    sys.exit(main())

