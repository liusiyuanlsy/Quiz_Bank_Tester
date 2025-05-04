import tkinter as tk
from tkinter import ttk
import os
import time
from config.settings import UI_FONT_FAMILY, UI_NORMAL_FONT_SIZE

class FileSelectionView:
    """文件选择对话框"""

    def __init__(self, parent, files, controller):
        """
        初始化文件选择对话框

        Args:
            parent: 父窗口
            files: 文件列表
            controller: 控制器对象
        """
        self.parent = parent
        self.files = files
        self.controller = controller
        self.selected_file = ""

        self._create_dialog()

    def _create_dialog(self):
        """创建对话框"""
        self.dialog = self.parent
        self.dialog.title("选择题库文件")
        self.dialog.geometry("400x400")  # 增加窗口高度，确保按钮可见
        self.dialog.resizable(False, False)  # 禁止调整大小

        # 设置窗口关闭事件处理
        self.dialog.protocol("WM_DELETE_WINDOW", self._on_cancel)

        # 说明标签文本根据文件数量调整
        label_text = "找到以下题库文件，请选择要使用的文件："
        if len(self.files) == 1:
            label_text = "找到一个题库文件，点击确认使用或取消重新选择："

        # 添加提示文字标签
        ttk.Label(
            self.dialog,
            text="请将题库文件放在桌面或程序文件夹下",
            font=(UI_FONT_FAMILY, UI_NORMAL_FONT_SIZE),
            foreground="#666666",
            wraplength=380
        ).pack(pady=(10, 0), padx=20)

        ttk.Label(
            self.dialog,
            text=label_text,
            font=(UI_FONT_FAMILY, UI_NORMAL_FONT_SIZE, 'bold'),
            wraplength=380
        ).pack(pady=(20, 10), padx=20)

        # 创建一个包含列表框和滚动条的容器框架
        list_frame = ttk.Frame(self.dialog)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # 创建列表框
        self.file_listbox = tk.Listbox(
            list_frame,
            font=(UI_FONT_FAMILY, UI_NORMAL_FONT_SIZE),
            height=10,
            selectmode=tk.SINGLE,
            activestyle='dotbox'
        )
        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 创建滚动条并正确放置
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.file_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.file_listbox.configure(yscrollcommand=scrollbar.set)

        # 添加文件到列表
        for file in self.files:
            # 获取文件名（不含路径）用于显示
            file_name = os.path.basename(file)
            self.file_listbox.insert(tk.END, file_name)

            # 获取完整路径和文件信息
            full_path = file
            if os.path.exists(full_path):
                file_size = os.path.getsize(full_path) / 1024  # KB
                mod_time = os.path.getmtime(full_path)
                mod_time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(mod_time))
                file_info = f"路径: {full_path}\n大小: {file_size:.1f} KB\n修改时间: {mod_time_str}"
                # 设置提示文本，悬停时显示
                # 注意：Tkinter的Listbox没有直接设置提示的功能，这里只是预留，如需实现可能需要自定义组件

        # 默认选择第一个文件
        if self.files:
            self.file_listbox.selection_set(0)
            self.file_listbox.activate(0)
            self.file_listbox.see(0)

        # 按钮区域
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(pady=20, side=tk.BOTTOM)  # 使用side=BOTTOM确保按钮在底部

        confirm_btn = ttk.Button(button_frame, text="确认", command=self._on_confirm, width=10)
        confirm_btn.pack(side=tk.LEFT, padx=10)
        cancel_btn = ttk.Button(button_frame, text="取消", command=self._on_cancel, width=10)
        cancel_btn.pack(side=tk.LEFT, padx=10)

        # 设置默认按钮（按回车激活）
        self.dialog.bind('<Return>', lambda event: self._on_confirm())
        self.dialog.bind('<Escape>', lambda event: self._on_cancel())

        # 双击事件处理
        self.file_listbox.bind('<Double-1>', lambda event: self._on_confirm())

        # 将焦点设置到列表框
        self.file_listbox.focus_set()

    def show(self):
        """显示对话框"""
        self.dialog.mainloop()

    def _on_confirm(self):
        """确认按钮点击事件"""
        selected_indices = self.file_listbox.curselection()
        if selected_indices:
            self.selected_file = self.files[selected_indices[0]]
            self.dialog.destroy()
            # 加载选中的题库文件
            self.controller.load_question_bank(self.selected_file)

    def _on_cancel(self):
        """取消按钮点击事件"""
        self.selected_file = ""
        self.dialog.destroy()
        # 退出应用程序
        self.controller.exit_application()

    def get_selected_file(self):
        """
        获取选择的文件

        Returns:
            str: 选择的文件路径，如果取消则返回空字符串
        """
        return self.selected_file