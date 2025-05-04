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

import tkinter as tk
from models.question_bank import QuestionBank
from services.file_service import FileService
from services.parser_service import ParserService
from utils.logger import get_logger

class AppController:
    """
    应用程序主控制器类

    负责应用程序的核心逻辑，包括：
    - 题库文件的加载和管理
    - 题目的显示和导航
    - 答案检查和记录
    - 用户设置的处理
    """

    def __init__(self, view=None):
        """
        初始化应用程序主控制器

        Args:
            view: 视图对象
        """
        self.logger = get_logger()
        self.view = view
        self.file_service = FileService()
        self.parser_service = ParserService()
        self.question_bank = None
        self.random_mode = False
        self.save_records = True  # 默认保存做题记录

    def set_view(self, view):
        """
        设置视图

        Args:
            view: 视图对象
        """
        self.view = view

    def start(self):
        """
        启动应用程序

        Returns:
            bool: 是否成功启动
        """
        # 隐藏主窗口（做题窗口）
        self.view.root.withdraw()

        # 直接使用系统文件选择器
        file_path = self.file_service._open_file_dialog(self, direct_load=True)

        # 如果用户取消选择，退出应用
        if file_path is None:
            self.view.destroy()
            return False

        # 如果已成功加载题库文件（返回"loaded"），则正常启动应用程序
        if file_path == "loaded":
            return True

        # 其他情况（例如选择了文件但加载失败）
        # 重新尝试选择文件
        self.reselect_question_bank()
        return True

    def load_question_bank(self, bank_file):
        """
        加载题库文件

        Args:
            bank_file (str): 题库文件路径
        """
        if not bank_file:
            self.exit_application()
            return

        # 加载题库
        try:
            questions = self.parser_service.parse_document(bank_file)
            self.question_bank = QuestionBank(questions, bank_file)

            # 显示做题窗口
            self.view.root.deiconify()

            # 更新题库路径显示
            self.view.update_file_path(bank_file)

            # 显示第一题
            self.show_current_question()
        except Exception as e:
            self.logger.error(f"加载题库失败: {str(e)}")
            self.view.show_error("错误", f"加载题库失败: {str(e)}\n\n请确保选择的是正确格式的题库文件。")

            # 重新选择题库文件，而不是退出应用程序
            self.reselect_question_bank()

    def show_current_question(self):
        """显示当前题目"""
        if not self.question_bank:
            return

        question = self.question_bank.get_current_question()
        if question:
            self.view.question_frame.display_question(question)
            self.view.feedback_frame.reset()
            self.view.update_status(
                self.question_bank.current_index + 1,
                self.question_bank.get_question_count()
            )

            # 更新做题统计信息
            self._update_stats()

            # 如果有用户答案，显示
            user_answer = self.question_bank.get_user_answer(self.question_bank.current_index)
            if user_answer:
                self.view.question_frame.set_selected_answer(user_answer)
                self.check_answer(user_answer)

    def next_question(self):
        """下一题"""
        if self.question_bank:
            # 如果不保存做题记录，则在切换题目时清空用户答案
            if not self.save_records:
                self.question_bank.user_answers = {}

            self.question_bank.next_question(self.random_mode)
            self.show_current_question()

    def prev_question(self):
        """上一题"""
        if self.question_bank:
            # 如果不保存做题记录，则在切换题目时清空用户答案
            if not self.save_records:
                self.question_bank.user_answers = {}

            self.question_bank.prev_question(self.random_mode)
            self.show_current_question()

    def jump_to_question(self, question_num):
        """
        跳转到指定题号的题目

        对输入的题号进行验证，确保其在有效范围内，然后跳转到对应题目。
        如果题号不合法，显示错误信息。

        Args:
            question_num (int): 要跳转到的题目编号（从1开始）

        Returns:
            bool: 跳转成功返回True，失败返回False
        """
        if self.question_bank:
            try:
                # 将题号转换为索引（题号从1开始，索引从0开始）
                index = int(question_num) - 1

                # 验证索引是否在有效范围内
                if 0 <= index < self.question_bank.get_question_count():
                    # 如果不保存做题记录，则在切换题目时清空用户答案
                    if not self.save_records:
                        self.question_bank.user_answers = {}

                    # 执行跳转并显示题目
                    self.question_bank.jump_to_question(index)
                    self.show_current_question()
                    return True
                else:
                    # 题号超出范围，显示错误信息
                    self.view.show_error(
                        "错误",
                        f"请输入1-{self.question_bank.get_question_count()}之间的题号"
                    )
            except ValueError:
                # 输入无法转换为整数，显示错误
                self.view.show_error("错误", "请输入有效的题号数字")
        return False

    def check_answer(self, user_answer):
        """
        检查答案

        Args:
            user_answer (str): 用户答案
        """
        if not self.question_bank:
            return

        question = self.question_bank.get_current_question()
        if question:
            # 保存用户答案
            self.question_bank.save_user_answer(self.question_bank.current_index, user_answer)

            # 检查答案
            is_correct = question.check_answer(user_answer)
            self.view.feedback_frame.show_feedback(
                is_correct,
                user_answer,
                question.answer,
                question.explanation
            )

            # 更新做题统计信息
            self._update_stats()

    def toggle_random_mode(self, is_random):
        """
        切换随机模式

        Args:
            is_random (bool): 是否随机模式
        """
        self.random_mode = is_random

    def set_save_records(self, save_records):
        """
        设置是否保存做题记录

        Args:
            save_records (bool): 是否保存做题记录
        """
        self.save_records = save_records

        # 如果取消保存做题记录，则清空所有用户答案
        if not save_records and self.question_bank:
            self.question_bank.user_answers = {}
            self.show_current_question()

    def _update_stats(self):
        """更新做题统计信息"""
        if not self.question_bank:
            return

        # 计算统计信息
        total_answered = len(self.question_bank.user_answers)
        correct_count = self.question_bank.get_correct_count()
        incorrect_count = total_answered - correct_count

        # 更新导航框架中的统计信息显示
        self.view.navigation_frame.update_stats(
            total_answered,
            correct_count,
            incorrect_count
        )

    def reselect_question_bank(self):
        """重新选取题库"""
        # 清空做题记录
        if self.question_bank:
            self.question_bank.user_answers = {}

        # 隐藏做题窗口
        self.view.root.withdraw()

        # 直接使用系统文件选择器
        file_path = self.file_service._open_file_dialog(self, direct_load=True)

        # 如果用户取消选择，显示原窗口
        if file_path is None:
            self.view.root.deiconify()
        # 如果已成功加载题库文件（返回"loaded"），窗口显示已由load_question_bank处理
        # 其他情况（例如选择了文件但加载失败）不需要特殊处理

    def exit_application(self):
        """退出应用程序"""
        if self.view:
            self.view.destroy()
        # 确保程序完全退出
        import sys
        sys.exit(0)