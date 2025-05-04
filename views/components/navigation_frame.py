import tkinter as tk
from tkinter import ttk, messagebox
from config.settings import UI_FONT_FAMILY, UI_NORMAL_FONT_SIZE

class NavigationFrame:
    """导航控制组件"""

    def __init__(self, parent, controller):
        """
        初始化导航控制组件

        Args:
            parent: 父窗口
            controller: 控制器对象
        """
        self.parent = parent
        self.controller = controller

        # 获取视图中的保存做题记录变量
        if hasattr(parent, 'save_records_var'):
            self.save_records_var = parent.save_records_var
        else:
            self.save_records_var = tk.BooleanVar(value=True)

        self._create_widgets()

    def _create_widgets(self):
        """创建组件"""
        # 导航控制区域
        control_frame = ttk.Frame(self.parent)
        control_frame.pack(pady=10, fill=tk.X)

        # 上一题/下一题按钮
        nav_frame = ttk.Frame(control_frame)
        nav_frame.pack(side=tk.LEFT, padx=10)

        self.btn_prev = ttk.Button(
            nav_frame,
            text="上一题",
            command=self._on_prev_click,
            width=10
        )
        self.btn_prev.grid(row=0, column=0, padx=5)

        self.btn_next = ttk.Button(
            nav_frame,
            text="下一题",
            command=self._on_next_click,
            width=10
        )
        self.btn_next.grid(row=0, column=1, padx=5)

        # 随机模式复选框
        self.random_var = tk.BooleanVar()
        self.random_check = ttk.Checkbutton(
            control_frame,
            text="随机抽题",
            variable=self.random_var,
            command=self._on_random_toggle
        )
        self.random_check.pack(side=tk.LEFT, padx=(10, 5))

        # 保存做题记录复选框
        self.save_records_check = ttk.Checkbutton(
            control_frame,
            text="保存做题记录",
            variable=self.save_records_var,
            command=self._on_save_records_toggle
        )
        self.save_records_check.pack(side=tk.LEFT, padx=5)

        # 做题统计信息显示
        self.stats_label = ttk.Label(
            control_frame,
            text="",
            font=(UI_FONT_FAMILY, UI_NORMAL_FONT_SIZE)
        )
        self.stats_label.pack(side=tk.LEFT, padx=10)

        # 跳转题号输入框
        jump_frame = ttk.Frame(control_frame)
        jump_frame.pack(side=tk.RIGHT, padx=10)

        ttk.Label(jump_frame, text="跳转到:").pack(side=tk.LEFT)

        self.jump_entry = ttk.Entry(jump_frame, width=8)
        self.jump_entry.pack(side=tk.LEFT, padx=5)

        ttk.Button(
            jump_frame,
            text="跳转",
            command=self._on_jump_click,
            width=6
        ).pack(side=tk.LEFT)

    def _on_prev_click(self):
        """上一题按钮点击事件"""
        self.controller.prev_question()

    def _on_next_click(self):
        """下一题按钮点击事件"""
        self.controller.next_question()

    def _on_random_toggle(self):
        """随机模式切换事件"""
        is_random = self.random_var.get()
        self.controller.toggle_random_mode(is_random)

    def _on_save_records_toggle(self):
        """保存做题记录切换事件"""
        save_records = self.save_records_var.get()
        self.controller.set_save_records(save_records)

        # 如果取消保存做题记录，清空统计信息显示
        if not save_records:
            self.stats_label.config(text="")

    def _on_jump_click(self):
        """跳转按钮点击事件"""
        try:
            question_num = int(self.jump_entry.get())
            if self.controller.jump_to_question(question_num):
                # 跳转成功后清空输入框
                self.jump_entry.delete(0, tk.END)
            else:
                messagebox.showerror("错误", "请输入有效的题号")
        except ValueError:
            messagebox.showerror("错误", "请输入有效的题号数字")

    def set_random_mode(self, is_random):
        """
        设置随机模式

        Args:
            is_random (bool): 是否随机模式
        """
        self.random_var.set(is_random)

    def update_stats(self, total_answered, correct_count, incorrect_count):
        """
        更新做题统计信息

        Args:
            total_answered (int): 已做题目数量
            correct_count (int): 正确题目数量
            incorrect_count (int): 错误题目数量
        """
        if self.save_records_var.get():
            self.stats_label.config(
                text=f"已做{total_answered}题，{correct_count}道正确，{incorrect_count}道错误"
            )
        else:
            self.stats_label.config(text="")