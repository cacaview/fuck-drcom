"""
配置文件 - Dr.COM网络共享系统

⚠️ 免责声明：
本软件仅供学习和技术研究使用。使用本软件即表示您已阅读、理解并同意遵守完整的
《免责声明》（详见项目根目录下的"免责声明.md"文件）。

使用本软件产生的一切法律问题和后果由使用者自行承担，开发者不承担任何法律义务。
请严格遵守相关法律法规和学校网络使用规定。

发布日期：2025年11月7日
"""

# Dr.COM认证服务器配置
DRCOM_CONFIG = {
    'base_url': 'http://10.252.252.5',
    'eportal_port': 801,
    'login_path': '/eportal/',
    'login_params': {
        'c': 'ACSetting',
        'a': 'Login',
    },
    'logout_params': {
        'c': 'ACSetting',
        'a': 'Logout',
        'ver': '1.0',
    },
    'status_path': '/drcom/chkstatus',
    'user_field': 'DDDDD',  # 账号字段名
    'pass_field': 'upass',  # 密码字段名
    # 设备类型配置
    # ⚠️ 重要：固定为PC设备类型('1')，避免被其他设备踢下线
    # 不管实际是什么类型的设备（手机、平板、PC），都向验证服务器提交PC设备类型
    # 设备类型：'1'=PC, '2'=手机, '3'=其他
    'terminal_type': '1',  # 固定为PC设备类型
}

# 登录重试配置
RETRY_CONFIG = {
    'max_retries': 5,       # 最大重试次数
    'retry_delay': 30,      # 重试延迟（秒）
    'ping_timeout': 5,      # ping超时时间（秒）
    'test_url': 'www.bing.com',  # 测试网络连通性的地址
}

# VPN服务配置
VPN_CONFIG = {
    'server_port': 8888,    # VPN服务端口
    'local_proxy_port': 1080,  # 客户端本地SOCKS5代理端口
    'heartbeat_interval': 30,  # 心跳间隔（秒）
    'buffer_size': 8192,    # 缓冲区大小
    'connection_timeout': 10,  # 连接超时（秒）
    'socks5_enabled': True,  # 启用SOCKS5代理（真实流量转发）
}

# 日志配置
LOG_CONFIG = {
    'log_dir': 'logs',
    'log_level': 'DEBUG',
    'max_bytes': 10 * 1024 * 1024,  # 10MB
    'backup_count': 5,
}

