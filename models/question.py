class Question:
    """题目模型类，表示一个考试题目"""

    def __init__(self, text="", options=None, answer="", explanation=""):
        """
        初始化题目对象

        Args:
            text (str): 题目文本
            options (list): 选项列表
            answer (str): 正确答案（A、B、C、D）
            explanation (str): 题目解析
        """
        self.text = text
        self.options = options or []
        self.answer = answer
        self.explanation = explanation

    def is_complete(self):
        """
        检查题目是否完整（有题目文本、选项和答案）

        Returns:
            bool: 题目是否完整
        """
        return bool(self.text and self.options and self.answer)

    def check_answer(self, user_answer):
        """
        检查用户答案是否正确

        Args:
            user_answer (str): 用户选择的答案

        Returns:
            bool: 答案是否正确
        """
        return user_answer.upper() == self.answer.upper()

    def __str__(self):
        """返回题目的字符串表示"""
        return f"题目: {self.text[:30]}..., 答案: {self.answer}"