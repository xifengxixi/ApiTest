import logging
import colorlog
import os,sys
sys.path.append(os.getcwd())
from datetime import datetime
from common.yaml_util import get_object_path,read_config

class LogUtil:

    def create_log(self, logger_name='log'):
        # 创建一个日志对象
        self.logger = logging.getLogger(logger_name)
        # 设置全局的日志级别 DEBUG < INFO < WARNING < ERROR < CRITICAL
        self.logger.setLevel(logging.DEBUG)
        # 设置日志级别对应颜色
        self.log_colors_config = {
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red'
        }
        # 防止日志重复
        if not self.logger.handlers:
            # ----------文件日志----------
            # 获得文件日志的名称并设置名称格式
            self.file_log_path = get_object_path()+'/logs/'+read_config('log', 'log_name')+'_'+str(datetime.now().strftime('%Y%m%d-%H%M'))+'.log'
            # 创建文件日志的控制器
            self.file_hander = logging.FileHandler(self.file_log_path, encoding='utf-8')
            # 设置文件日志的级别
            file_log_level = str(read_config('log', 'log_level')).lower()
            if file_log_level == 'debug':
                self.file_hander.setLevel(logging.DEBUG)
            elif file_log_level == 'info':
                self.file_hander.setLevel(logging.INFO)
            elif file_log_level == 'warning':
                self.file_hander.setLevel(logging.WARNING)
            elif file_log_level == 'error':
                self.file_hander.setLevel(logging.ERROR)
            elif file_log_level == 'critical':
                self.file_hander.setLevel(logging.CRITICAL)
            # 设置文件日志的格式
            self.file_hander.setFormatter(logging.Formatter(read_config('log', 'log_format')))
            # 将文件日志控制器加入到日志对象
            self.logger.addHandler(self.file_hander)
            
            # ----------控制台日志----------
            # 创建控制台日志的控制器
            self.console_hander = logging.StreamHandler()
            # 设置控制台日志的级别
            console_log_level = str(read_config('log', 'log_level')).lower()
            if console_log_level == 'debug':
                self.console_hander.setLevel(logging.DEBUG)
            elif console_log_level == 'info':
                self.console_hander.setLevel(logging.INFO)
            elif console_log_level == 'warning':
                self.console_hander.setLevel(logging.WARNING)
            elif console_log_level == 'error':
                self.console_hander.setLevel(logging.ERROR)
            elif console_log_level == 'critical':
                self.console_hander.setLevel(logging.CRITICAL)
            # 设置控制台日志的格式
            file_log_format = read_config('log', 'log_format')
            console_log_format = '%(log_color)s'+file_log_format
            format = colorlog.ColoredFormatter(console_log_format, log_colors=self.log_colors_config)
            self.console_hander.setFormatter(format)
            # 将控制台日志控制器加入到日志对象
            self.logger.addHandler(self.console_hander)
        return self.logger

logger = LogUtil().create_log()

if __name__ == '__main__':
    logger.debug("这是一个debug信息")
    logger.info("这是一个info信息")
    logger.warning("这是一个warning信息")
    logger.error("这是一个error信息")
    logger.critical("这是一个critical信息")