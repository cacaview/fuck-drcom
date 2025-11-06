"""
配置文件 - Dr.COM网络共享系统

⚠️ 免责声明：
此软件仅供学习用途使用，使用此软件则代表您愿意承担所造成的法律问题，
开发者不为此承担任何法律义务。
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
    'heartbeat_interval': 30,  # 心跳间隔（秒）
    'buffer_size': 8192,    # 缓冲区大小
}

# 日志配置
LOG_CONFIG = {
    'log_dir': 'logs',
    'log_level': 'DEBUG',
    'max_bytes': 10 * 1024 * 1024,  # 10MB
    'backup_count': 5,
}

