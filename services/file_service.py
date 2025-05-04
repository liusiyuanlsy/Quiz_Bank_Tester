import os
import sys
import time
import tkinter as tk
from tkinter import filedialog
from utils.logger import get_logger
from config.settings import FILE_PATTERNS, FILE_KEYWORDS

class FileService:
    """文件服务，负责文件操作"""

    def __init__(self):
        """初始化文件服务"""
        self.logger = get_logger()

    def find_question_banks(self, controller=None):
        """
        在程序所在目录和桌面搜索题库文件，如果都没找到则打开文件选择器

        Args:
            controller: 控制器对象，用于控制窗口显示

        Returns:
            list: 题库文件路径列表
        """
        bank_files = []

        # 获取主程序目录
        main_dir = self._get_main_directory()
        self.logger.info(f"搜索题库文件，主程序目录: {main_dir}")

        # 获取桌面目录
        desktop_dir = self._get_desktop_directory()

        # 在主程序目录中搜索
        if main_dir and os.path.exists(main_dir):
            bank_files.extend(self._search_directory(main_dir, False, "主程序"))

        # 在桌面目录中搜索
        if desktop_dir and os.path.exists(desktop_dir):
            bank_files.extend(self._search_directory(desktop_dir, True))
        else:
            self.logger.warning(f"桌面目录不存在或无法访问: {desktop_dir}")

        # 如果没有找到题库文件，打开文件选择器
        if not bank_files:
            self.logger.info("未在主程序目录和桌面找到题库文件，打开文件选择器")
            manual_file = self._open_file_dialog(controller)
            if manual_file:
                bank_files.append(manual_file)

        self.logger.info(f"共找到 {len(bank_files)} 个题库文件")
        return bank_files

    def _get_main_directory(self):
        """
        获取主程序目录

        Returns:
            str: 主程序目录路径
        """
        if getattr(sys, 'frozen', False):
            # 运行于 exe 模式
            return os.path.dirname(sys.executable)
        else:
            # 运行于脚本模式
            # 获取当前工作目录，而不是文件所在目录
            return os.getcwd()

    def _get_desktop_directory(self):
        """
        获取桌面目录

        Returns:
            str: 桌面目录路径，如果获取失败则返回None
        """
        try:
            desktop_dir = os.path.join(os.path.expanduser("~"), "Desktop")
            if not desktop_dir.endswith(os.path.sep):
                desktop_dir += os.path.sep
            self.logger.info(f"额外搜索桌面目录: {desktop_dir}")
            return desktop_dir
        except Exception as e:
            self.logger.error(f"获取桌面路径时出错: {str(e)}")
            return None

    def _search_directory(self, directory, is_desktop=False, dir_type="程序"):
        """
        在指定目录中搜索题库文件

        Args:
            directory (str): 目录路径
            is_desktop (bool): 是否是桌面目录
            dir_type (str): 目录类型描述，用于日志

        Returns:
            list: 找到的文件路径列表
        """
        result = []
        try:
            for file in os.listdir(directory):
                file_lower = file.lower()
                # 检查文件是否符合条件
                is_match = False
                for pattern in FILE_PATTERNS:
                    if file_lower.endswith(pattern):
                        for keyword in FILE_KEYWORDS:
                            if keyword in file or file_lower == f"{keyword}{pattern}":
                                is_match = True
                                break
                        if is_match:
                            break

                if is_match:
                    full_path = os.path.join(directory, file)
                    if os.path.exists(full_path):
                        file_size = os.path.getsize(full_path) / 1024  # KB
                        log_prefix = "在桌面" if is_desktop else ""
                        self.logger.info(f"{log_prefix}找到题库文件: {file} (大小: {file_size:.1f} KB)")

                        # 始终添加完整路径
                        result.append(full_path)
        except Exception as e:
            self.logger.error(f"搜索{dir_type}目录时出错: {str(e)}")

        return result

    def get_file_info(self, file_path):
        """
        获取文件信息

        Args:
            file_path (str): 文件路径

        Returns:
            dict: 文件信息字典，包含路径、名称、大小和修改时间
        """
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path) / 1024  # KB
            mod_time = os.path.getmtime(file_path)
            mod_time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(mod_time))
            return {
                "path": file_path,
                "name": os.path.basename(file_path),
                "size": f"{file_size:.1f} KB",
                "modified": mod_time_str
            }
        return None

    def _open_file_dialog(self, controller=None):
        """
        打开文件选择对话框，让用户手动选择题库文件

        Args:
            controller: 控制器对象，用于控制窗口显示

        Returns:
            str: 选择的文件路径，如果取消则返回None
        """
        try:
            # 创建临时的根窗口
            root = tk.Tk()
            root.withdraw()  # 隐藏窗口

            # 打开文件选择对话框
            file_path = filedialog.askopenfilename(
                title="选择题库文件",
                filetypes=[("Word文档", "*.docx"), ("所有文件", "*.*")]
            )

            # 销毁临时窗口
            root.destroy()

            if file_path:
                self.logger.info(f"用户手动选择了题库文件: {file_path}")
                return file_path
            else:
                self.logger.info("用户取消了手动选择题库文件")
                return None
        except Exception as e:
            self.logger.error(f"打开文件选择对话框时出错: {str(e)}")
            return None