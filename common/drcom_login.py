"""
Dr.COM登录模块 - 模拟网页登录校园网

⚠️ 免责声明：
本软件仅供学习和技术研究使用。使用本软件即表示您已阅读、理解并同意遵守完整的
《免责声明》（详见项目根目录下的"免责声明.md"文件）。

使用本软件产生的一切法律问题和后果由使用者自行承担，开发者不承担任何法律义务。
请严格遵守相关法律法规和学校网络使用规定。

发布日期：2025年11月7日
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
    
    def __init__(self, username, password, isp='中国电信', connection_type='auto'):
        """
        初始化登录管理器
        
        Args:
            username: 用户名
            password: 密码
            isp: 运营商类型，可选值：'中国电信'、'中国移动'、'中国联通'、'中国广电'、'职工账号'
            connection_type: 连接方式，可选值：'auto'(自动检测)、'wifi'(WiFi)、'wired'(有线)
        """
        self.username = username
        self.password = password
        self.isp = isp
        self.connection_type = connection_type
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
        
        # WiFi环境参数
        self.wifi_params = {
            'wlan_user_mac': '000000000000',
            'wlan_ac_ip': '',
            'wlan_ac_name': ''
        }
    
    def get_wifi_params_from_redirect(self):
        """
        获取WiFi环境参数（MAC地址、AC IP、AC名称）
        
        模拟网页的 term.init() 逻辑：
        1. 访问外网触发AC重定向（不自动跟随）
        2. 手动获取重定向的Location，其中包含WiFi参数
        3. 从重定向URL中提取参数
        
        Returns:
            dict: 包含 wlan_user_mac, wlan_ac_ip, wlan_ac_name 的字典
        """
        try:
            # 尝试多个测试URL，触发AC重定向
            test_urls = [
                'http://www.baidu.com',
                'http://www.msftconnecttest.com/connecttest.txt',
                'http://detectportal.firefox.com/success.txt',
                'http://captive.apple.com/hotspot-detect.html',
            ]
            
            for test_url in test_urls:
                try:
                    self.logger.debug(f"尝试访问 {test_url} 以触发AC重定向...")
                    
                    # 关键：不自动跟随重定向
                    response = self.session.get(
                        test_url,
                        allow_redirects=False,
                        timeout=5
                    )
                    
                    self.logger.debug(f"响应状态码: {response.status_code}")
                    
                    # 检查是否有重定向
                    if response.status_code in [301, 302, 303, 307, 308]:
                        redirect_url = response.headers.get('Location', '')
                        self.logger.debug(f"检测到重定向: {redirect_url}")
                        
                        if redirect_url:
                            # 如果是相对路径，补全为完整URL
                            if not redirect_url.startswith('http'):
                                redirect_url = f"http://10.252.252.5{redirect_url}"
                            
                            self.logger.debug(f"重定向URL: {redirect_url}")
                            
                            # 检查重定向是否到认证页面
                            if '10.252.252.5' in redirect_url or 'dr.com' in redirect_url.lower():
                                # 从重定向URL中提取WiFi参数
                                self._extract_wifi_params_from_url(redirect_url)
                                
                                if self.wifi_params['wlan_user_mac'] != '000000000000':
                                    self.logger.info(f"✓ 成功从AC重定向获取WiFi参数")
                                    self.logger.info(f"  重定向URL: {redirect_url}")
                                    return self.wifi_params
                                
                                # 如果第一层重定向没有参数，跟随一次看看
                                try:
                                    response2 = self.session.get(redirect_url, allow_redirects=True, timeout=5)
                                    final_url = response2.url
                                    self.logger.debug(f"最终URL: {final_url}")
                                    
                                    self._extract_wifi_params_from_url(final_url)
                                    if self.wifi_params['wlan_user_mac'] != '000000000000':
                                        self.logger.info(f"✓ 成功从最终重定向URL获取WiFi参数")
                                        return self.wifi_params
                                except Exception as e2:
                                    self.logger.debug(f"跟随重定向失败: {e2}")
                    
                except requests.exceptions.Timeout:
                    self.logger.debug(f"访问 {test_url} 超时")
                    continue
                except requests.exceptions.ConnectionError as e:
                    self.logger.debug(f"访问 {test_url} 连接错误: {e}")
                    continue
                except Exception as e:
                    self.logger.debug(f"访问 {test_url} 失败: {e}")
                    continue
            
            # 如果所有测试URL都失败，说明可能是有线连接或者已经登录
            self.logger.info("未能从AC重定向获取WiFi参数")
            self.logger.info("可能原因: 已登录、有线连接或AC未拦截")
            return self.wifi_params
                
        except Exception as e:
            self.logger.error(f"获取WiFi参数异常: {e}")
            return self.wifi_params
    
    def _extract_wifi_params_from_url(self, url):
        """
        从URL中提取WiFi参数
        
        Args:
            url: 包含WiFi参数的URL
        """
        # 提取MAC地址 (支持多种参数名格式)
        mac_patterns = [
            r'usermac=([0-9a-fA-F\-:]+)',
            r'wlan_user_mac=([0-9a-fA-F\-:]+)',
            r'mac=([0-9a-fA-F\-:]+)'
        ]
        for pattern in mac_patterns:
            match = re.search(pattern, url, re.IGNORECASE)
            if match:
                mac = match.group(1).replace('-', '').replace(':', '').lower()
                if mac and mac != '000000000000':
                    self.wifi_params['wlan_user_mac'] = mac
                    self.logger.debug(f"提取到MAC地址: {mac}")
                break
        
        # 提取AC IP
        ac_ip_patterns = [
            r'wlanacip=(\d+\.\d+\.\d+\.\d+)',
            r'wlan_ac_ip=(\d+\.\d+\.\d+\.\d+)',
            r'acip=(\d+\.\d+\.\d+\.\d+)'
        ]
        for pattern in ac_ip_patterns:
            match = re.search(pattern, url, re.IGNORECASE)
            if match:
                self.wifi_params['wlan_ac_ip'] = match.group(1)
                self.logger.debug(f"提取到AC IP: {match.group(1)}")
                break
        
        # 提取AC名称
        ac_name_patterns = [
            r'wlanacname=([^&]+)',
            r'wlan_ac_name=([^&]+)',
            r'acname=([^&]+)'
        ]
        for pattern in ac_name_patterns:
            match = re.search(pattern, url, re.IGNORECASE)
            if match:
                self.wifi_params['wlan_ac_name'] = match.group(1)
                self.logger.debug(f"提取到AC名称: {match.group(1)}")
                break
        
    def get_local_ip(self):
        """
        获取本机内网IP地址
        
        Returns:
            str: IP地址，格式如 '172.21.77.34'
        """
        try:
            # 尝试通过访问认证页面获取IP
            response = self.session.get(self.base_url, timeout=10)
            
            # 方法1: 查找 v4ip='172.21.77.34' 这样的模式
            ip_pattern = r"v4ip='(\d+\.\d+\.\d+\.\d+)'"
            match = re.search(ip_pattern, response.text)
            if match:
                ip = match.group(1)
                self.logger.info(f"从v4ip获取到IP: {ip}")
                return ip
            
            # 方法2: 从lip变量获取
            lip_pattern = r"lip='(\d+\.\d+\.\d+\.\d+)'"
            match = re.search(lip_pattern, response.text)
            if match:
                ip = match.group(1)
                self.logger.info(f"从lip获取到IP: {ip}")
                return ip
            
            # 方法3: 从URL参数中获取 (ip=172.21.77.57)
            url_ip_pattern = r'[?&]ip=(\d+\.\d+\.\d+\.\d+)'
            match = re.search(url_ip_pattern, response.text)
            if match:
                ip = match.group(1)
                self.logger.info(f"从URL参数获取到IP: {ip}")
                return ip
            
            # 方法4: 查找所有内网IP地址，选择最可能的一个
            # 内网IP通常以 10.x, 172.16-31.x, 或 192.168.x 开头
            all_ips = re.findall(r'\b(\d+\.\d+\.\d+\.\d+)\b', response.text)
            for ip in all_ips:
                # 过滤掉服务器自己的IP和回环地址
                if ip.startswith('10.252.252.'):
                    continue
                if ip.startswith('127.'):
                    continue
                # 检查是否为内网IP
                if (ip.startswith('10.') or 
                    ip.startswith('192.168.') or 
                    (ip.startswith('172.') and 16 <= int(ip.split('.')[1]) <= 31)):
                    self.logger.info(f"从页面内容获取到IP: {ip}")
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
    
    def test_internet_connection(self, max_retries=10, retry_interval=2):
        """
        测试是否可以访问互联网
        
        Args:
            max_retries: 最大重试次数
            retry_interval: 重试间隔（秒）
        
        Returns:
            bool: True表示可以访问互联网
        """
        test_url = RETRY_CONFIG['test_url']
        
        for attempt in range(1, max_retries + 1):
            try:
                self.logger.debug(f"网络连通性测试 ({attempt}/{max_retries}): ping {test_url}")
                
                # 根据操作系统选择ping命令参数
                param = '-n' if platform.system().lower() == 'windows' else '-c'
                
                # 执行ping命令
                result = subprocess.run(
                    ['ping', param, '1', test_url],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=RETRY_CONFIG['ping_timeout']
                )
                
                if result.returncode == 0:
                    self.logger.info(f"✓ 网络连通性测试成功 (第{attempt}次尝试)")
                    return True
                else:
                    if attempt < max_retries:
                        self.logger.debug(f"Ping失败，{retry_interval}秒后重试...")
                        time.sleep(retry_interval)
                    else:
                        self.logger.warning(f"网络连通性测试失败，已尝试{max_retries}次")
                        return False
                
            except subprocess.TimeoutExpired:
                if attempt < max_retries:
                    self.logger.debug(f"Ping超时，{retry_interval}秒后重试...")
                    time.sleep(retry_interval)
                else:
                    self.logger.warning(f"网络连通性测试超时，已尝试{max_retries}次")
                    return False
            except Exception as e:
                self.logger.error(f"测试网络连通性异常: {e}")
                if attempt < max_retries:
                    time.sleep(retry_interval)
                else:
                    return False
        
        return False
    
    def login(self):
        """
        执行登录操作
        
        Returns:
            dict: 登录结果，包含 'success'(bool), 'message'(str), 'ip'(str)
        """
        try:
            self.logger.info(f"开始登录，用户名: {self.username}, 运营商: {self.isp}")
            self.logger.info(f"连接方式: {self.connection_type}")
            
            # 根据连接方式决定是否获取WiFi参数
            if self.connection_type == 'wired':
                self.logger.info("使用有线连接模式，跳过WiFi参数检测")
            elif self.connection_type == 'wifi':
                self.logger.info("使用WiFi连接模式，开始获取WiFi参数...")
                self.get_wifi_params_from_redirect()
            else:  # auto
                self.logger.info("自动检测模式，尝试获取WiFi参数...")
                self.get_wifi_params_from_redirect()
            
            # 获取本机IP地址
            local_ip = self.get_local_ip()
            if not local_ip:
                self.logger.error("无法获取本机IP地址")
                return {
                    'success': False,
                    'message': '无法获取本机IP地址',
                    'ip': None
                }
            
            # 构造用户账号（格式：,0,username@isp_code）
            isp_code = DRCOM_CONFIG['isp_mapping'].get(self.isp, 'telecom')
            if isp_code:
                user_account = f',0,{self.username}@{isp_code}'
            else:
                user_account = f',0,{self.username}'
            
            self.logger.info(f"user_account: {user_account}, local_ip: {local_ip}")
            self.logger.info(f"WiFi参数 - MAC: {self.wifi_params['wlan_user_mac']}, "
                           f"AC IP: {self.wifi_params['wlan_ac_ip']}, "
                           f"AC Name: {self.wifi_params['wlan_ac_name']}")
            
            # 准备登录参数（所有参数通过URL query string传递）
            params = {
                'callback': 'dr1003',
                'login_method': '1',
                'user_account': user_account,
                'user_password': self.password,
                'wlan_user_ip': local_ip,
                'wlan_user_ipv6': '',
                'wlan_user_mac': self.wifi_params['wlan_user_mac'],
                'wlan_ac_ip': self.wifi_params['wlan_ac_ip'],
                'wlan_ac_name': self.wifi_params['wlan_ac_name'],
                'jsVersion': DRCOM_CONFIG['js_version'],
                'terminal_type': DRCOM_CONFIG['terminal_type'],
                'lang': 'zh-cn',
                'v': str(int(time.time() * 1000))
            }
            
            # 发送登录请求（使用GET方法）
            self.logger.debug(f"发送登录请求到: {self.eportal_url}")
            self.logger.debug(f"登录参数: {params}")
            
            response = self.session.get(
                self.eportal_url,
                params=params,
                timeout=10
            )
            
            self.logger.debug(f"登录响应状态码: {response.status_code}")
            self.logger.debug(f"登录响应完整内容: {response.text}")
            self.logger.info(f"登录响应预览: {response.text[:200]}")
            
            # 解析JSONP响应
            # 格式：dr1003({"result":1,"message":"success",...})
            jsonp_pattern = r'dr\d+\((.*)\)'
            match = re.search(jsonp_pattern, response.text)
            
            if match:
                import json
                try:
                    data = json.loads(match.group(1))
                    result = data.get('result', 0)
                    # 兼容不同的响应字段名: message 或 msg
                    message = data.get('message') or data.get('msg', '未知错误')
                    
                    if result == 1:
                        self.logger.info(f"✓ Portal协议认证成功！内网IP: {local_ip}")
                        self.logger.info(f"等待网络建立，持续测试连通性...")
                
                        # Portal认证成功后，持续ping直到网络真正可用
                        # 最多尝试10次，每次间隔2秒（共20秒）
                        if self.test_internet_connection(max_retries=10, retry_interval=2):
                            return {
                                'success': True,
                                'message': '登录成功，网络可用',
                                'ip': local_ip
                            }
                        else:
                            self.logger.warning("Portal认证成功，但网络连通性测试失败")
                            self.logger.warning("这可能是正常的（双网卡环境、特定路由等）")
                            # 即使ping失败，Portal认证成功也应该返回成功
                            # 因为在双网卡环境下ping可能走错网卡
                            return {
                                'success': True,
                                'message': 'Portal认证成功（网络测试未通过，可能是环境配置原因）',
                                'ip': local_ip
                            }
                    else:
                        self.logger.error(f"登录失败: {message}")
                        return {
                            'success': False,
                            'message': message,
                            'ip': None
                        }
                except json.JSONDecodeError:
                    self.logger.error(f"无法解析登录响应: {response.text[:200]}")
                    return {
                        'success': False,
                        'message': '响应格式错误',
                        'ip': None
                    }
            else:
                # 无法解析响应
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
            
            logout_url = f"{self.base_url}:{DRCOM_CONFIG['eportal_port']}{DRCOM_CONFIG['logout_path']}"
            
            params = {
                'callback': 'dr1004',
                'jsVersion': DRCOM_CONFIG['js_version'],
                'v': str(int(time.time() * 1000))
            }
            
            response = self.session.get(
                logout_url,
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

