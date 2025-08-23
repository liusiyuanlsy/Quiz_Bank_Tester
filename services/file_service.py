"""
Copyright (c) 2025 Sylvan_930
基金考试题库系统 is licensed under Mulan PSL v2.
You can use this software according to the terms and conditions of the Mulan PSL v2.
You may obtain a copy of Mulan PSL v2 at:
         http://license.coscl.org.cn/MulanPSL2
THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND,
EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT,
MERCHANTABILITY OR FIT FOR A PARTICULAR PURPOSE.
See the Mulan PSL v2 for more details.
"""

import os
import sys
import time
import tkinter as tk
from tkinter import filedialog, messagebox
from utils.logger import get_logger
from config.settings import FILE_PATTERNS

class FileService:
    """文件服务类，负责文件选择和基本文件操作"""

    def __init__(self):
        """初始化文件服务，创建日志器实例"""
        self.logger = get_logger()

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
            return desktop_dir
        except Exception as e:
            self.logger.error(f"获取桌面路径时出错: {str(e)}")
            return None

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

    def _open_file_dialog(self, controller=None, direct_load=False):
        """
        打开系统文件选择对话框，让用户选择题库文件

        创建临时的根窗口显示文件选择对话框，并在选择后进行文件有效性检查。
        如果设置了direct_load参数，将直接调用控制器的load_question_bank方法加载文件。

        Args:
            controller: 控制器对象，用于调用加载题库方法
            direct_load: 是否直接加载选择的文件而不仅是返回路径

        Returns:
            str "loaded": 如果direct_load为True且成功加载文件
            str: 选择的文件路径，如果取消则返回None
            None: 如果用户取消选择或发生错误
        """
        try:
            # 创建临时的根窗口
            root = tk.Tk()
            root.withdraw()  # 隐藏窗口

            # 打开文件选择对话框
            file_path = filedialog.askopenfilename(
                title="选择题库文件",
                filetypes=[
                    ("所有文件", "*.*")  # 只保留所有文件选项
                ],
                initialdir=self._get_main_directory()  # 设置初始目录为主程序目录
            )

            # 销毁临时窗口
            root.destroy()

            if file_path:
                self.logger.info(f"用户选择了文件: {file_path}")

                # 确保文件存在
                if not os.path.exists(file_path):
                    self.logger.error(f"选择的文件不存在: {file_path}")
                    return None

                # 检查文件扩展名是否支持
                file_ext = os.path.splitext(file_path)[1].lower()
                if file_ext not in FILE_PATTERNS and file_ext != '':  # 空扩展名视为文件夹，跳过检查
                    self.logger.warning(f"选择的文件类型不受支持: {file_ext}")
                    # 创建临时的根窗口用于显示警告
                    warn_root = tk.Tk()
                    warn_root.withdraw()
                    messagebox.showwarning(
                        "文件类型警告",
                        f"选择的文件类型 {file_ext} 不在支持列表中，但系统仍将尝试加载。\n\n如果加载失败，请选择 .docx, .txt 或 .csv 格式的文件。"
                    )
                    warn_root.destroy()

                # 直接加载模式：调用控制器加载题库
                if direct_load and controller:
                    try:
                        controller.load_question_bank(file_path)
                        return "loaded"  # 返回特殊值表示已成功加载题库
                    except Exception as e:
                        self.logger.error(f"加载题库文件失败: {str(e)}")
                        # 加载失败时返回文件路径，允许控制器进行错误处理
                        return file_path
                else:
                    return file_path
            else:
                self.logger.info("用户取消了文件选择")
                return None
        except Exception as e:
            self.logger.error(f"打开文件选择对话框时出错: {str(e)}")
            return None