import tkinter as tk
from tkinter import ttk, messagebox
from views.components.question_frame import QuestionFrame
from views.components.feedback_frame import FeedbackFrame
from views.components.navigation_frame import NavigationFrame
from views.file_selection_view import FileSelectionView
from config.settings import APP_TITLE, WINDOW_SIZE, COLOR_STATUS_TEXT

class AppView:
    """应用程序主视图"""

    def __init__(self, controller):
        """
        初始化应用程序主视图

        Args:
            controller: 控制器对象
        """
        self.controller = controller
        self.root = tk.Tk()
        self.root.title(APP_TITLE)
        self.root.geometry(WINDOW_SIZE)

        self.configure_styles()
        self._create_widgets()

    def configure_styles(self):
        """配置界面样式"""
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('.', font=('微软雅黑', 10))
        style.configure('TButton', font=('微软雅黑', 10))
        style.configure('TRadiobutton', font=('微软雅黑', 12))
        style.configure('TLabel', font=('微软雅黑', 10))
        style.map('TRadiobutton',
                background=[('selected', '#c1e1c1'), ('!selected', 'white')],
                foreground=[('selected', 'black'), ('!selected', 'black')])

    def _create_widgets(self):
        """创建组件"""
        # 创建组件
        self.question_frame = QuestionFrame(self.root, self.controller)
        self.feedback_frame = FeedbackFrame(self.root, self.controller)
        self.navigation_frame = NavigationFrame(self.root, self.controller)

        # 初始化保存做题记录变量，供导航框架使用
        self.save_records_var = tk.BooleanVar(value=True)

        # 题库路径显示和重新选取按钮区域
        file_path_frame = ttk.Frame(self.root)
        file_path_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=(0, 2))

        self.file_path_label = ttk.Label(
            file_path_frame,
            text="题库路径: 未加载",
            foreground=COLOR_STATUS_TEXT,
            anchor='w'
        )
        self.file_path_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # 重新选取题库按钮
        self.reselect_btn = ttk.Button(
            file_path_frame,
            text="重新选取题库",
            command=self._on_reselect_bank
        )
        self.reselect_btn.pack(side=tk.RIGHT, padx=5)

        # 状态栏
        self.status_bar = ttk.Label(
            self.root,
            text="0/0",
            foreground=COLOR_STATUS_TEXT
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X, pady=5)

    def show_file_selection_dialog(self, files):
        """
        显示文件选择对话框

        Args:
            files: 文件列表

        Returns:
            str: 选择的文件路径，如果取消则返回空字符串
        """
        # 注意：此方法已不再使用，保留是为了兼容性
        # 文件选择现在由 AppController 直接处理
        return ""

    def update_file_path(self, file_path):
        """
        更新题库文件路径显示

        Args:
            file_path (str): 题库文件路径
        """
        if file_path:
            self.file_path_label.config(text=f"题库路径: {file_path}")
        else:
            self.file_path_label.config(text="题库路径: 未加载")

    def update_status(self, current, total):
        """
        更新状态栏

        Args:
            current (int): 当前题目索引
            total (int): 题目总数
        """
        self.status_bar.config(text=f"第 {current}/{total} 题")

    def show_error(self, title, message):
        """
        显示错误消息

        Args:
            title (str): 错误标题
            message (str): 错误消息
        """
        messagebox.showerror(title, message)

    def show_info(self, title, message):
        """
        显示信息消息

        Args:
            title (str): 信息标题
            message (str): 信息消息
        """
        messagebox.showinfo(title, message)

    def start(self):
        """启动应用程序"""
        self.root.mainloop()

    def destroy(self):
        """销毁应用程序窗口"""
        self.root.destroy()

    def _on_save_records_changed(self):
        """保存做题记录勾选框状态变化事件"""
        save_records = self.save_records_var.get()
        self.controller.set_save_records(save_records)

    def get_save_records_state(self):
        """
        获取保存做题记录勾选框状态

        Returns:
            bool: 是否保存做题记录
        """
        return self.save_records_var.get()

    def _on_reselect_bank(self):
        """重新选取题库按钮点击事件"""
        self.controller.reselect_question_bank()