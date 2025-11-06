"""
VPN客户�?- Flet GUI版本
支持多平台：Windows、Linux、macOS、Android、iOS、Web
"""

import flet as ft
import threading
import time
from client.vpn_client import VPNClient
from common.config import VPN_CONFIG
from common.logger import Logger


class VPNClientGUI:
    """VPN客户端图形界�?""
    
    def __init__(self, page: ft.Page):
        """初始化GUI"""
        self.page = page
        self.page.title = "Dr.COM VPN 客户�?
        self.page.window_width = 500
        self.page.window_height = 700
        self.page.window_resizable = False
        self.page.padding = 20
        
        self.logger = Logger('VPNClientGUI', 'vpn_client_gui')
        self.client = None
        self.client_thread = None
        
        # 创建UI组件
        self._create_ui()
    
    def _create_ui(self):
        """创建用户界面"""
        
        # 标题
        title = ft.Text(
            "Dr.COM VPN 客户�?,
            size=28,
            weight=ft.FontWeight.BOLD,
            color=ft.colors.BLUE_700
        )
        
        # 说明文字
        description = ft.Text(
            "连接到VPN服务器以共享网络资源",
            size=14,
            color=ft.colors.GREY_700
        )
        
        # 用户名输�?
        self.username_field = ft.TextField(
            label="Dr.COM 用户�?,
            hint_text="例如: MR646C80105795",
            prefix_icon=ft.icons.PERSON,
            width=400
        )
        
        # 密码输入
        self.password_field = ft.TextField(
            label="Dr.COM 密码",
            hint_text="请输入密�?,
            prefix_icon=ft.icons.LOCK,
            password=True,
            can_reveal_password=True,
            width=400
        )
        
        # 服务器IP输入
        self.server_ip_field = ft.TextField(
            label="服务器内网IP",
            hint_text="例如: 172.21.77.34",
            prefix_icon=ft.icons.COMPUTER,
            width=400
        )
        
        # 服务器端口输�?
        self.server_port_field = ft.TextField(
            label="服务器端�?,
            hint_text=str(VPN_CONFIG['server_port']),
            value=str(VPN_CONFIG['server_port']),
            prefix_icon=ft.icons.PORT,
            width=400,
            keyboard_type=ft.KeyboardType.NUMBER
        )
        
        # 连接按钮
        self.connect_button = ft.ElevatedButton(
            "连接",
            icon=ft.icons.POWER,
            on_click=self._on_connect_click,
            width=200,
            height=50,
            style=ft.ButtonStyle(
                color=ft.colors.WHITE,
                bgcolor=ft.colors.GREEN_700,
            )
        )
        
        # 断开按钮
        self.disconnect_button = ft.ElevatedButton(
            "断开",
            icon=ft.icons.POWER_OFF,
            on_click=self._on_disconnect_click,
            width=200,
            height=50,
            disabled=True,
            style=ft.ButtonStyle(
                color=ft.colors.WHITE,
                bgcolor=ft.colors.RED_700,
            )
        )
        
        # 状态显�?
        self.status_text = ft.Text(
            "未连�?,
            size=16,
            weight=ft.FontWeight.BOLD,
            color=ft.colors.GREY_700
        )
        
        # 日志显示区域
        self.log_list = ft.ListView(
            spacing=5,
            padding=10,
            auto_scroll=True,
            height=250
        )
        
        # 日志容器
        log_container = ft.Container(
            content=self.log_list,
            border=ft.border.all(1, ft.colors.GREY_400),
            border_radius=5,
            padding=5
        )
        
        # 组装界面
        self.page.add(
            ft.Column([
                title,
                description,
                ft.Divider(height=20),
                self.username_field,
                self.password_field,
                self.server_ip_field,
                self.server_port_field,
                ft.Divider(height=10),
                ft.Row([
                    self.connect_button,
                    self.disconnect_button
                ], alignment=ft.MainAxisAlignment.CENTER),
                ft.Divider(height=10),
                ft.Row([
                    ft.Text("状�? ", size=16),
                    self.status_text
                ]),
                ft.Divider(height=10),
                ft.Text("运行日志:", size=14, weight=ft.FontWeight.BOLD),
                log_container
            ], spacing=10)
        )
    
    def _add_log(self, message, color=ft.colors.BLACK):
        """
        添加日志
        
        Args:
            message: 日志消息
            color: 文字颜色
        """
        timestamp = time.strftime("%H:%M:%S")
        log_item = ft.Text(
            f"[{timestamp}] {message}",
            size=12,
            color=color
        )
        self.log_list.controls.append(log_item)
        
        # 限制日志条数（防止内存占用过大）
        if len(self.log_list.controls) > 100:
            self.log_list.controls.pop(0)
        
        self.page.update()
    
    def _update_status(self, status, color):
        """
        更新状态显�?
        
        Args:
            status: 状态文�?
            color: 颜色
        """
        self.status_text.value = status
        self.status_text.color = color
        self.page.update()
    
    def _on_connect_click(self, e):
        """连接按钮点击事件"""
        # 验证输入
        if not self.username_field.value:
            self._add_log("错误: 请输入用户名", ft.colors.RED)
            return
        
        if not self.password_field.value:
            self._add_log("错误: 请输入密�?, ft.colors.RED)
            return
        
        if not self.server_ip_field.value:
            self._add_log("错误: 请输入服务器IP", ft.colors.RED)
            return
        
        try:
            port = int(self.server_port_field.value)
        except:
            self._add_log("错误: 端口号必须是数字", ft.colors.RED)
            return
        
        # 禁用连接按钮，启用断开按钮
        self.connect_button.disabled = True
        self.disconnect_button.disabled = False
        self.page.update()
        
        # 在新线程中启动客户端
        self.client_thread = threading.Thread(
            target=self._run_client,
            daemon=True
        )
        self.client_thread.start()
    
    def _on_disconnect_click(self, e):
        """断开按钮点击事件"""
        if self.client:
            self._add_log("正在断开连接...", ft.colors.ORANGE)
            self.client.stop()
            self.client = None
        
        # 恢复按钮状�?
        self.connect_button.disabled = False
        self.disconnect_button.disabled = True
        self._update_status("已断开", ft.colors.GREY_700)
        self.page.update()
    
    def _run_client(self):
        """在后台线程中运行客户�?""
        try:
            # 更新状�?
            self._update_status("正在连接...", ft.colors.ORANGE)
            self._add_log("=== 开始连�?===", ft.colors.BLUE)
            
            # 创建客户�?
            username = self.username_field.value
            password = self.password_field.value
            server_ip = self.server_ip_field.value
            server_port = int(self.server_port_field.value)
            
            self.client = VPNClient(username, password, server_ip, server_port)
            
            # 重定向日志到GUI
            self._redirect_logger()
            
            # 启动客户�?
            self._add_log(f"用户�? {username}", ft.colors.GREY_700)
            self._add_log(f"服务�? {server_ip}:{server_port}", ft.colors.GREY_700)
            
            if self.client.start():
                self._update_status("已连�?, ft.colors.GREEN_700)
                self._add_log("�?连接成功�?, ft.colors.GREEN)
            else:
                self._update_status("连接失败", ft.colors.RED)
                self._add_log("�?连接失败", ft.colors.RED)
                
                # 恢复按钮状�?
                self.connect_button.disabled = False
                self.disconnect_button.disabled = True
                self.page.update()
                
        except Exception as ex:
            self._add_log(f"错误: {str(ex)}", ft.colors.RED)
            self._update_status("发生错误", ft.colors.RED)
            
            # 恢复按钮状�?
            self.connect_button.disabled = False
            self.disconnect_button.disabled = True
            self.page.update()
    
    def _redirect_logger(self):
        """重定向日志输出到GUI"""
        # 这是一个简化版本，实际应该使用日志处理�?
        original_info = self.client.logger.info
        original_warning = self.client.logger.warning
        original_error = self.client.logger.error
        
        def gui_info(msg):
            original_info(msg)
            self._add_log(msg, ft.colors.BLACK)
        
        def gui_warning(msg):
            original_warning(msg)
            self._add_log(msg, ft.colors.ORANGE)
        
        def gui_error(msg):
            original_error(msg)
            self._add_log(msg, ft.colors.RED)
        
        self.client.logger.info = gui_info
        self.client.logger.warning = gui_warning
        self.client.logger.error = gui_error


def main(page: ft.Page):
    """主函�?""
    VPNClientGUI(page)


if __name__ == '__main__':
    ft.app(target=main)

