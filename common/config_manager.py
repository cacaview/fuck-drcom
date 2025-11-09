"""
加密配置管理模块 - 安全存储用户配置

⚠️ 免责声明：
本软件仅供学习和技术研究使用。使用本软件即表示您已阅读、理解并同意遵守完整的
《免责声明》（详见项目根目录下的"免责声明.md"文件）。

使用本软件产生的一切法律问题和后果由使用者自行承担，开发者不承担任何法律义务。
请严格遵守相关法律法规和学校网络使用规定。

发布日期：2025年11月7日
"""

import os
import json
import getpass
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64


class ConfigManager:
    """加密配置管理器"""
    
    def __init__(self, config_file='config.encrypted'):
        """
        初始化配置管理器
        
        Args:
            config_file: 加密配置文件名
        """
        self.config_file = config_file
        self.config_dir = '.drcom'
        self.config_path = os.path.join(self.config_dir, config_file)
        
        # 确保配置目录存在
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)
    
    def _derive_key(self, password: str, salt: bytes) -> bytes:
        """
        从密码派生加密密钥
        
        Args:
            password: 用户密码
            salt: 盐值
            
        Returns:
            bytes: 派生的密钥
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000
        )
        return base64.urlsafe_b64encode(kdf.derive(password.encode()))
    
    def save_config(self, config: dict, master_password: str = None) -> bool:
        """
        保存加密配置
        
        Args:
            config: 配置字典
            master_password: 主密码（用于加密），如果为None则提示输入
            
        Returns:
            bool: 是否成功
        """
        try:
            # 如果没有提供主密码，提示用户输入
            if master_password is None:
                print("\n🔐 设置主密码（用于保护您的配置文件）")
                master_password = getpass.getpass("请输入主密码: ")
                confirm_password = getpass.getpass("请再次输入确认: ")
                
                if master_password != confirm_password:
                    print("❌ 两次输入的密码不一致！")
                    return False
                
                if len(master_password) < 6:
                    print("❌ 主密码长度至少6位！")
                    return False
            
            # 生成随机盐值
            salt = os.urandom(16)
            
            # 派生加密密钥
            key = self._derive_key(master_password, salt)
            fernet = Fernet(key)
            
            # 序列化配置
            config_json = json.dumps(config)
            
            # 加密配置
            encrypted_data = fernet.encrypt(config_json.encode())
            
            # 保存到文件（盐值 + 加密数据）
            with open(self.config_path, 'wb') as f:
                f.write(salt + encrypted_data)
            
            # 设置文件权限（仅所有者可读写）
            if os.name != 'nt':  # Unix/Linux/macOS
                os.chmod(self.config_path, 0o600)
            
            print(f"✓ 配置已加密保存到: {self.config_path}")
            return True
            
        except Exception as e:
            print(f"❌ 保存配置失败: {e}")
            return False
    
    def load_config(self, master_password: str = None) -> dict:
        """
        加载加密配置
        
        Args:
            master_password: 主密码，如果为None则提示输入
            
        Returns:
            dict: 配置字典，失败返回None
        """
        try:
            # 检查配置文件是否存在
            if not os.path.exists(self.config_path):
                return None
            
            # 如果没有提供主密码，提示用户输入
            if master_password is None:
                master_password = getpass.getpass("🔐 请输入主密码解锁配置: ")
            
            # 读取文件
            with open(self.config_path, 'rb') as f:
                data = f.read()
            
            # 提取盐值和加密数据
            salt = data[:16]
            encrypted_data = data[16:]
            
            # 派生密钥
            key = self._derive_key(master_password, salt)
            fernet = Fernet(key)
            
            # 解密数据
            decrypted_data = fernet.decrypt(encrypted_data)
            
            # 反序列化配置
            config = json.loads(decrypted_data.decode())
            
            print("✓ 配置已成功解密加载")
            return config
            
        except Exception as e:
            print(f"❌ 加载配置失败: {e}")
            print("提示: 可能是主密码错误或配置文件损坏")
            return None
    
    def config_exists(self) -> bool:
        """
        检查配置文件是否存在
        
        Returns:
            bool: 配置文件是否存在
        """
        return os.path.exists(self.config_path)
    
    def delete_config(self) -> bool:
        """
        删除配置文件
        
        Returns:
            bool: 是否成功
        """
        try:
            if os.path.exists(self.config_path):
                os.remove(self.config_path)
                print("✓ 配置文件已删除")
                return True
            return False
        except Exception as e:
            print(f"❌ 删除配置失败: {e}")
            return False


def interactive_input() -> dict:
    """
    交互式输入配置
    
    Returns:
        dict: 配置字典
    """
    print("\n" + "=" * 60)
    print("📝 配置信息输入")
    print("=" * 60)
    
    config = {}
    
    # 输入用户名
    while True:
        username = input("Dr.COM 用户名: ").strip()
        if username:
            config['username'] = username
            break
        print("❌ 用户名不能为空！")
    
    # 输入密码（隐藏显示）
    while True:
        password = getpass.getpass("Dr.COM 密码: ")
        if password:
            confirm_password = getpass.getpass("确认密码: ")
            if password == confirm_password:
                config['password'] = password
                break
            else:
                print("❌ 两次输入的密码不一致，请重新输入！")
        else:
            print("❌ 密码不能为空！")
    
    # 选择运营商
    print("\n选择运营商类型:")
    print("  1. 中国电信 (默认)")
    print("  2. 中国移动")
    print("  3. 中国联通")
    print("  4. 中国广电")
    print("  5. 职工账号")
    
    isp_options = {
        '1': '中国电信',
        '2': '中国移动',
        '3': '中国联通',
        '4': '中国广电',
        '5': '职工账号'
    }
    
    while True:
        isp_choice = input("请选择 [1]: ").strip()
        if not isp_choice:
            isp_choice = '1'
        if isp_choice in isp_options:
            config['isp'] = isp_options[isp_choice]
            print(f"✓ 已选择: {config['isp']}")
            break
        else:
            print("❌ 无效选择，请输入 1-5！")
    
    # 选择连接方式
    print("\n选择连接方式:")
    print("  1. 自动检测 (默认)")
    print("  2. WiFi 连接")
    print("  3. 有线连接")
    print()
    print("说明:")
    print("  - WiFi连接：需要获取MAC地址和AC信息，适用于校园WiFi")
    print("  - 有线连接：跳过WiFi参数检测，直接登录，速度更快")
    print("  - 自动检测：尝试获取WiFi参数，如果失败则使用默认值")
    
    connection_options = {
        '1': 'auto',
        '2': 'wifi',
        '3': 'wired'
    }
    
    connection_names = {
        'auto': '自动检测',
        'wifi': 'WiFi连接',
        'wired': '有线连接'
    }
    
    while True:
        conn_choice = input("请选择 [1]: ").strip()
        if not conn_choice:
            conn_choice = '1'
        if conn_choice in connection_options:
            config['connection_type'] = connection_options[conn_choice]
            print(f"✓ 已选择: {connection_names[config['connection_type']]}")
            break
        else:
            print("❌ 无效选择，请输入 1-3！")
    
    return config


def interactive_input_server() -> dict:
    """
    交互式输入服务器配置
    
    Returns:
        dict: 配置字典
    """
    config = interactive_input()
    
    # 输入端口
    while True:
        port_str = input("服务端口 [默认: 8888]: ").strip()
        if not port_str:
            config['port'] = 8888
            break
        try:
            port = int(port_str)
            if 1024 <= port <= 65535:
                config['port'] = port
                break
            else:
                print("❌ 端口号必须在 1024-65535 之间！")
        except ValueError:
            print("❌ 请输入有效的端口号！")
    
    return config


def interactive_input_client() -> dict:
    """
    交互式输入客户端配置
    
    Returns:
        dict: 配置字典
    """
    config = interactive_input()
    
    # 输入服务器IP
    while True:
        server_ip = input("服务器内网IP: ").strip()
        if server_ip:
            config['server_ip'] = server_ip
            break
        print("❌ 服务器IP不能为空！")
    
    # 输入端口
    while True:
        port_str = input("服务器端口 [默认: 8888]: ").strip()
        if not port_str:
            config['port'] = 8888
            break
        try:
            port = int(port_str)
            if 1024 <= port <= 65535:
                config['port'] = port
                break
            else:
                print("❌ 端口号必须在 1024-65535 之间！")
        except ValueError:
            print("❌ 请输入有效的端口号！")
    
    return config


if __name__ == '__main__':
    # 测试代码
    print("配置管理器测试")
    
    manager = ConfigManager('test_config.encrypted')
    
    # 测试保存
    test_config = {
        'username': 'testuser',
        'password': 'testpass123',
        'server_ip': '192.168.1.100',
        'port': 8888
    }
    
    if manager.save_config(test_config, 'test_master_password'):
        print("保存成功")
        
        # 测试加载
        loaded_config = manager.load_config('test_master_password')
        if loaded_config:
            print("加载成功:", loaded_config)
        
        # 清理测试文件
        manager.delete_config()


