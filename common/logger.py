"""
日志模块 - 提供详细的日志记录功能

⚠️ 免责声明：
本软件仅供学习和技术研究使用。使用本软件即表示您已阅读、理解并同意遵守完整的
《免责声明》（详见项目根目录下的"免责声明.md"文件）。

使用本软件产生的一切法律问题和后果由使用者自行承担，开发者不承担任何法律义务。
请严格遵守相关法律法规和学校网络使用规定。

发布日期：2025年11月7日
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime
from .config import LOG_CONFIG


class Logger:
    """日志管理器"""
    
    def __init__(self, name, log_file=None):
        """
        初始化日志记录器
        
        Args:
            name: 日志记录器名称
            log_file: 日志文件名（可选）
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, LOG_CONFIG['log_level']))
        
        # 避免重复添加handler
        if not self.logger.handlers:
            # 创建日志目录
            if not os.path.exists(LOG_CONFIG['log_dir']):
                os.makedirs(LOG_CONFIG['log_dir'])
            
            # 日志格式
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            
            # 控制台处理器
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
            
            # 文件处理器（如果指定了日志文件）
            if log_file:
                log_path = os.path.join(
                    LOG_CONFIG['log_dir'],
                    f"{log_file}_{datetime.now().strftime('%Y%m%d')}.log"
                )
                file_handler = RotatingFileHandler(
                    log_path,
                    maxBytes=LOG_CONFIG['max_bytes'],
                    backupCount=LOG_CONFIG['backup_count'],
                    encoding='utf-8'
                )
                file_handler.setLevel(logging.DEBUG)
                file_handler.setFormatter(formatter)
                self.logger.addHandler(file_handler)
    
    def debug(self, msg):
        """记录调试信息"""
        self.logger.debug(msg)
    
    def info(self, msg):
        """记录一般信息"""
        self.logger.info(msg)
    
    def warning(self, msg):
        """记录警告信息"""
        self.logger.warning(msg)
    
    def error(self, msg):
        """记录错误信息"""
        self.logger.error(msg)
    
    def critical(self, msg):
        """记录严重错误信息"""
        self.logger.critical(msg)

