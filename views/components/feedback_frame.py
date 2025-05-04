import tkinter as tk
from tkinter import ttk
from config.settings import (
    UI_FONT_FAMILY,
    UI_FEEDBACK_FONT_SIZE,
    UI_EXPLANATION_FONT_SIZE,
    COLOR_CORRECT,
    COLOR_INCORRECT,
    COLOR_BACKGROUND
)

class FeedbackFrame:
    """反馈区域组件"""

    def __init__(self, parent, controller):
        """
        初始化反馈区域组件

        Args:
            parent: 父窗口
            controller: 控制器对象
        """
        self.parent = parent
        self.controller = controller

        self._create_widgets()

    def _create_widgets(self):
        """创建组件"""
        # 反馈区域
        self.feedback_frame = ttk.Frame(self.parent)
        self.feedback_frame.pack(pady=5, fill=tk.X, padx=20)

        # 反馈标签
        self.lbl_feedback = ttk.Label(
            self.feedback_frame,
            font=(UI_FONT_FAMILY, UI_FEEDBACK_FONT_SIZE, 'bold'),
            wraplength=650
        )
        self.lbl_feedback.pack(anchor='w')

        # 解析文本框
        self.txt_explanation = tk.Text(
            self.feedback_frame,
            height=4,
            wrap=tk.WORD,
            font=(UI_FONT_FAMILY, UI_EXPLANATION_FONT_SIZE),
            state='disabled',
            background=COLOR_BACKGROUND,
            padx=10,
            pady=5
        )
        self.txt_explanation.pack(fill=tk.X, pady=5)

    def reset(self):
        """重置反馈区域"""
        self.lbl_feedback.config(text="")
        self.txt_explanation.config(state='normal')
        self.txt_explanation.delete(1.0, tk.END)
        self.txt_explanation.config(state='disabled')

    def show_feedback(self, is_correct, user_answer, correct_answer, explanation=""):
        """
        显示反馈信息

        Args:
            is_correct (bool): 是否回答正确
            user_answer (str): 用户答案
            correct_answer (str): 正确答案
            explanation (str): 题目解析
        """
        # 先重置反馈区域
        self.reset()

        # 设置反馈文本
        if is_correct:
            self.lbl_feedback.config(
                text=f"✅ 回答正确！正确答案是：{correct_answer}",
                foreground=COLOR_CORRECT
            )
        else:
            self.lbl_feedback.config(
                text=f"❌ 回答错误！您的选择：{user_answer}，正确答案：{correct_answer}",
                foreground=COLOR_INCORRECT
            )

        # 显示解析
        if explanation:
            self.txt_explanation.config(state='normal')
            self.txt_explanation.insert(tk.END, "【题目解析】\n" + explanation)
            self.txt_explanation.config(state='disabled')