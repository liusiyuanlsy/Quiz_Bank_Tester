import os
import sys
import time
import tkinter as tk
from tkinter import filedialog, messagebox
from utils.logger import get_logger
from config.settings import FILE_PATTERNS

class FileService:
    """文件服务，负责文件操作"""

    def __init__(self):
        """初始化文件服务"""
        self.logger = get_logger()

    # 删除 find_question_banks 方法，不再需要自动搜索题库文件

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

    # 删除 _search_directory 方法，不再需要搜索目录

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
        打开文件选择对话框，让用户手动选择题库文件

        Args:
            controller: 控制器对象，用于控制窗口显示
            direct_load: 是否直接加载选择的文件

        Returns:
            str: 选择的文件路径，如果取消则返回None
            None: 如果direct_load为True且成功加载文件，则返回None
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

                # 如果是直接加载模式，则直接调用控制器的加载方法
                if direct_load and controller:
                    try:
                        controller.load_question_bank(file_path)
                        return "loaded"  # 返回特殊值表示已成功加载
                    except Exception as e:
                        self.logger.error(f"加载题库文件失败: {str(e)}")
                        # 如果加载失败，返回文件路径，让控制器处理错误
                        return file_path
                else:
                    return file_path
            else:
                self.logger.info("用户取消了文件选择")
                return None
        except Exception as e:
            self.logger.error(f"打开文件选择对话框时出错: {str(e)}")
            return None