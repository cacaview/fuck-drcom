"""
Dr.COM登录模块 - 模拟网页登录校园网

⚠️ 免责声明：
此软件仅供学习用途使用，使用此软件则代表您愿意承担所造成的法律问题，
开发者不为此承担任何法律义务。
"""

import requests
import re
import time
import subprocess
import platform
from urllib.parse import urljoin
from .config import DRCOM_CONFIG, RETRY_CONFIG
from .logger import Logger


class DrcomLogin:
    """Dr.COM登录管理器"""
    
    def __init__(self, username, password):
        """
        初始化登录管理器
        
        Args:
            username: 用户名
            password: 密码
        """
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.logger = Logger('DrcomLogin', 'drcom_login')
        
        # 设置请求头，模拟浏览器
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
        })
        
        self.base_url = DRCOM_CONFIG['base_url']
        self.eportal_url = f"{self.base_url}:{DRCOM_CONFIG['eportal_port']}{DRCOM_CONFIG['login_path']}"
        
    def get_local_ip(self):
        """
        获取本机内网IP地址
        
        Returns:
            str: IP地址，格式如 '172.21.77.34'
        """
        try:
            # 尝试通过访问认证页面获取IP
            response = self.session.get(self.base_url, timeout=5)
            
            # 从页面中提取IP信息
            # 查找 v4ip='172.21.77.34' 这样的模式
            ip_pattern = r"v4ip='(\d+\.\d+\.\d+\.\d+)'"
            match = re.search(ip_pattern, response.text)
            if match:
                ip = match.group(1)
                self.logger.info(f"从认证页面获取到IP: {ip}")
                return ip
            
            # 备用方案：从lip变量获取
            lip_pattern = r"lip='(\d+\.\d+\.\d+\.\d+)'"
            match = re.search(lip_pattern, response.text)
            if match:
                ip = match.group(1)
                self.logger.info(f"从lip变量获取到IP: {ip}")
                return ip
                
        except Exception as e:
            self.logger.error(f"获取IP地址失败: {e}")
        
        return None
    
    def check_network_status(self):
        """
        检查网络状态
        
        Returns:
            dict: 状态信息，包含 'online'(bool) 和 'message'(str)
        """
        try:
            # 方法1: 访问chkstatus接口
            status_url = urljoin(self.base_url, DRCOM_CONFIG['status_path'])
            response = self.session.get(status_url, timeout=5)
            
            self.logger.debug(f"状态查询响应: {response.text[:200]}")
            
            # 解析JSONP响应
            # 格式通常是: dr1001({...})
            jsonp_pattern = r'\w+\((.*)\)'
            match = re.search(jsonp_pattern, response.text)
            if match:
                import json
                data = json.loads(match.group(1))
                
                # result=1 表示在线, result=0 表示离线
                if data.get('result') == 1:
                    self.logger.info("网络状态: 已在线")
                    return {'online': True, 'message': '已在线', 'data': data}
                else:
                    self.logger.info("网络状态: 离线")
                    return {'online': False, 'message': '离线', 'data': data}
        
        except Exception as e:
            self.logger.error(f"检查网络状态失败: {e}")
        
        return {'online': False, 'message': '状态未知'}
    
    def test_internet_connection(self):
        """
        测试是否可以访问互联网
        
        Returns:
            bool: True表示可以访问互联网
        """
        try:
            self.logger.debug(f"测试网络连通性: ping {RETRY_CONFIG['test_url']}")
            
            # 根据操作系统选择ping命令参数
            param = '-n' if platform.system().lower() == 'windows' else '-c'
            
            # 执行ping命令
            result = subprocess.run(
                ['ping', param, '1', RETRY_CONFIG['test_url']],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=RETRY_CONFIG['ping_timeout']
            )
            
            success = result.returncode == 0
            self.logger.info(f"网络连通性测试: {'成功' if success else '失败'}")
            return success
            
        except Exception as e:
            self.logger.error(f"测试网络连通性异常: {e}")
            return False
    
    def login(self):
        """
        执行登录操作
        
        Returns:
            dict: 登录结果，包含 'success'(bool), 'message'(str), 'ip'(str)
        """
        try:
            self.logger.info(f"开始登录，用户名: {self.username}")
            
            # 准备登录数据
            login_data = {
                DRCOM_CONFIG['user_field']: self.username,
                DRCOM_CONFIG['pass_field']: self.password,
                'callback': 'dr1001',
                'login_method': '1',
                'wlan_user_ip': '',
                'wlan_user_ipv6': '',
                'wlan_user_mac': '000000000000',
                'wlan_ac_ip': '',
                'wlan_ac_name': '',
                'jsVersion': '4.X',
                'terminal_type': '1',
                'lang': 'zh',
                'v': str(int(time.time() * 1000))
            }
            
            # 添加URL参数
            params = DRCOM_CONFIG['login_params'].copy()
            
            # 发送登录请求
            response = self.session.get(
                self.eportal_url,
                params=params,
                data=login_data,
                timeout=10
            )
            
            self.logger.debug(f"登录响应: {response.text[:300]}")
            
            # 解析响应
            if '成功' in response.text or 'success' in response.text.lower():
                ip = self.get_local_ip()
                self.logger.info(f"登录成功！内网IP: {ip}")
                
                # 验证是否真的可以上网
                if self.test_internet_connection():
                    return {
                        'success': True,
                        'message': '登录成功，网络可用',
                        'ip': ip
                    }
                else:
                    self.logger.warning("登录成功但无法访问互联网，可能被其他设备踢下线")
                    return {
                        'success': False,
                        'message': '登录成功但无法访问互联网',
                        'ip': ip
                    }
            else:
                # 尝试从响应中提取错误信息
                error_msg = self._extract_error_message(response.text)
                self.logger.error(f"登录失败: {error_msg}")
                return {
                    'success': False,
                    'message': error_msg,
                    'ip': None
                }
        
        except Exception as e:
            self.logger.error(f"登录异常: {e}")
            return {
                'success': False,
                'message': f'登录异常: {str(e)}',
                'ip': None
            }
    
    def login_with_retry(self):
        """
        带重试机制的登录
        
        Returns:
            dict: 登录结果
        """
        max_retries = RETRY_CONFIG['max_retries']
        retry_delay = RETRY_CONFIG['retry_delay']
        
        for attempt in range(1, max_retries + 1):
            self.logger.info(f"第 {attempt}/{max_retries} 次登录尝试")
            
            result = self.login()
            
            if result['success']:
                return result
            
            # 如果还有重试机会，等待后重试
            if attempt < max_retries:
                self.logger.warning(
                    f"登录失败: {result['message']}, "
                    f"{retry_delay}秒后进行第{attempt + 1}次重试..."
                )
                time.sleep(retry_delay)
            else:
                self.logger.error(f"登录失败，已达到最大重试次数({max_retries})")
        
        return {
            'success': False,
            'message': f'登录失败，已重试{max_retries}次',
            'ip': None
        }
    
    def logout(self):
        """
        执行注销操作
        
        Returns:
            bool: 注销是否成功
        """
        try:
            self.logger.info("开始注销")
            
            params = DRCOM_CONFIG['logout_params'].copy()
            params['callback'] = 'dr1001'
            params['jsVersion'] = '4.X'
            params['v'] = str(int(time.time() * 1000))
            
            response = self.session.get(
                self.eportal_url,
                params=params,
                timeout=10
            )
            
            self.logger.debug(f"注销响应: {response.text[:200]}")
            self.logger.info("注销成功")
            return True
            
        except Exception as e:
            self.logger.error(f"注销异常: {e}")
            return False
    
    def _extract_error_message(self, html_text):
        """
        从响应中提取错误信息
        
        Args:
            html_text: HTML响应文本
            
        Returns:
            str: 错误信息
        """
        # 尝试提取常见错误信息
        error_patterns = [
            r'"msg":"([^"]+)"',
            r'"message":"([^"]+)"',
            r'<message>([^<]+)</message>',
        ]
        
        for pattern in error_patterns:
            match = re.search(pattern, html_text)
            if match:
                return match.group(1)
        
        return "未知错误"

