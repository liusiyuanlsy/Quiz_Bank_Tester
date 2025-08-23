import random

class QuestionBank:
    """题库模型类，管理题目集合"""

    def __init__(self, questions=None, file_path=None):
        """
        初始化题库对象

        Args:
            questions (list): 题目列表
            file_path (str): 题库文件路径
        """
        self.questions = questions or []
        self.file_path = file_path
        self.current_index = 0
        self.user_answers = {}  # 存储用户答案

    def add_question(self, question):
        """
        添加题目到题库

        Args:
            question (Question): 题目对象
        """
        self.questions.append(question)

    def get_question(self, index):
        """
        获取指定索引的题目

        Args:
            index (int): 题目索引

        Returns:
            Question: 题目对象，如果索引无效则返回None
        """
        if 0 <= index < len(self.questions):
            return self.questions[index]
        return None

    def get_current_question(self):
        """
        获取当前题目

        Returns:
            Question: 当前题目对象
        """
        return self.get_question(self.current_index)

    def next_question(self, random_mode=False):
        """
        移动到下一题

        Args:
            random_mode (bool): 是否随机模式

        Returns:
            Question: 下一题目对象
        """
        if random_mode:
            self.current_index = random.randint(0, len(self.questions) - 1)
        elif self.current_index < len(self.questions) - 1:
            self.current_index += 1
        return self.get_current_question()

    def prev_question(self, random_mode=False):
        """
        移动到上一题

        Args:
            random_mode (bool): 是否随机模式

        Returns:
            Question: 上一题目对象
        """
        if random_mode:
            self.current_index = random.randint(0, len(self.questions) - 1)
        elif self.current_index > 0:
            self.current_index -= 1
        return self.get_current_question()

    def jump_to_question(self, index):
        """
        跳转到指定题目

        Args:
            index (int): 题目索引

        Returns:
            Question: 跳转后的题目对象，如果索引无效则返回None
        """
        if 0 <= index < len(self.questions):
            self.current_index = index
            return self.get_current_question()
        return None

    def get_question_count(self):
        """
        获取题目总数

        Returns:
            int: 题目总数
        """
        return len(self.questions)

    def save_user_answer(self, index, answer):
        """
        保存用户答案

        Args:
            index (int): 题目索引
            answer (str): 用户答案
        """
        self.user_answers[index] = answer

    def get_user_answer(self, index):
        """
        获取用户答案

        Args:
            index (int): 题目索引

        Returns:
            str: 用户答案，如果没有回答则返回空字符串
        """
        return self.user_answers.get(index, "")

    def get_correct_count(self):
        """
        获取正确答案数量

        Returns:
            int: 正确答案数量
        """
        correct_count = 0
        for index, answer in self.user_answers.items():
            if index < len(self.questions) and answer == self.questions[index].answer:
                correct_count += 1
        return correct_count