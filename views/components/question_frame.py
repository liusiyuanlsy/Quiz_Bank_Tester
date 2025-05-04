import tkinter as tk
from tkinter import ttk
from utils.text_utils import hide_answer_in_text
from config.settings import UI_QUESTION_FONT_SIZE, UI_OPTION_FONT_SIZE, UI_FONT_FAMILY

class QuestionFrame:
    """题目显示组件"""

    def __init__(self, parent, controller):
        """
        初始化题目显示组件

        Args:
            parent: 父窗口
            controller: 控制器对象
        """
        self.parent = parent
        self.controller = controller

        self._create_widgets()

    def _create_widgets(self):
        """创建组件"""
        # 题目显示区域
        self.txt_question = tk.Text(
            self.parent,
            height=6,  # 减小高度以优化布局
            wrap=tk.WORD,
            font=(UI_FONT_FAMILY, UI_QUESTION_FONT_SIZE),
            spacing2=6,
            padx=10,
            pady=10
        )
        self.txt_question.pack(pady=5, padx=20, fill=tk.BOTH, expand=True)

        # 选项区域
        self.var_answer = tk.StringVar()
        self.radios = []
        self.radio_frame = ttk.Frame(self.parent)
        self.radio_frame.pack(pady=5, fill=tk.X)

        for i in range(4):
            rb = ttk.Radiobutton(
                self.radio_frame,
                text="",
                variable=self.var_answer,
                value=chr(65+i),
                command=self._on_answer_selected,
                style='TRadiobutton'
            )
            rb.grid(row=i, column=0, sticky="w", padx=30, pady=3)
            self.radios.append(rb)

    def _on_answer_selected(self):
        """选项选择事件处理"""
        answer = self.var_answer.get()
        if answer:
            self.controller.check_answer(answer)

    def display_question(self, question):
        """
        显示题目

        Args:
            question: 题目对象
        """
        if not question:
            return

        self.var_answer.set("")  # 重置选项状态

        # 隐藏答案
        display_text = hide_answer_in_text(question.text)

        # 更新题目文本
        self.txt_question.config(state='normal')
        self.txt_question.delete(1.0, tk.END)
        self.txt_question.insert(tk.END, display_text)
        self.txt_question.config(state='disabled')

        # 更新选项
        for i, radio in enumerate(self.radios):
            if i < len(question.options):
                radio.config(text=question.options[i], state='normal')
            else:
                radio.config(text="", state='disabled')

    def get_selected_answer(self):
        """
        获取用户选择的答案

        Returns:
            str: 用户选择的答案
        """
        return self.var_answer.get()

    def set_selected_answer(self, answer):
        """
        设置用户选择的答案

        Args:
            answer (str): 用户选择的答案
        """
        self.var_answer.set(answer)