import logging
import os
import sys
from config.settings import LOG_LEVEL, LOG_FILE

def get_logger():
    """
    获取日志记录器

    Returns:
        logging.Logger: 配置好的日志记录器
    """
    logger = logging.getLogger('quiz_bank')

    # 如果已经配置过，直接返回
    if logger.handlers:
        return logger

    # 配置日志级别
    log_level = getattr(logging, LOG_LEVEL, logging.INFO)
    logger.setLevel(log_level)

    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)

    # 创建文件处理器
    try:
        if getattr(sys, 'frozen', False):
            # 运行于 exe 模式
            log_dir = os.path.dirname(sys.executable)
        else:
            # 运行于脚本模式
            log_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        log_file = os.path.join(log_dir, LOG_FILE)
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(log_level)
    except Exception:
        file_handler = None

    # 创建格式化器
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    if file_handler:
        file_handler.setFormatter(formatter)

    # 添加处理器
    logger.addHandler(console_handler)
    if file_handler:
        logger.addHandler(file_handler)

    return logger