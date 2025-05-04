import re
import os
from docx import Document
from models.question import Question
from utils.logger import get_logger
from utils.text_utils import is_question_line, extract_answer_from_text

class ParserService:
    """文档解析服务，负责从Word文档中解析题目"""

    def __init__(self):
        """初始化解析服务"""
        self.logger = get_logger()

        # 定义各种正则表达式模式
        self.option_pattern = re.compile(r'^([A-D])[\.、:：]?\s*(.*)$')
        self.answer_pattern = re.compile(r'[（(]\s*([A-Da-d])\s*[）)]')
        self.empty_brackets_pattern = re.compile(r'[（(]\s*[）)]')
        self.question_num_pattern = re.compile(r'^\d+[\.、]|^第\d+题|^\d+、')

        # 多种独立答案行格式
        self.separate_answer_patterns = [
            re.compile(r'^答案[：:]\s*([A-Da-d])', re.IGNORECASE),
            re.compile(r'^答案[是为]?\s*([A-Da-d])', re.IGNORECASE),
            re.compile(r'^\s*([A-Da-d])\s*$', re.IGNORECASE),
            re.compile(r'^[（(]?\s*([A-Da-d])\s*[）)]?$', re.IGNORECASE),
            re.compile(r'.*[（(]\s*([A-Da-d])\s*[）)].*')
        ]

    def parse_document(self, file_path):
        """
        解析Word文档，提取题目

        Args:
            file_path (str): 文档路径

        Returns:
            list: 题目对象列表

        Raises:
            FileNotFoundError: 文件不存在
            ValueError: 文档格式错误
        """
        self.logger.info(f"开始解析文件: {file_path}")

        # 检查文件是否存在
        if not os.path.exists(file_path):
            self.logger.error(f"文件不存在: {file_path}")
            raise FileNotFoundError(f"文件不存在: {file_path}")

        # 打开文档
        try:
            doc = Document(file_path)
        except Exception as e:
            self.logger.error(f"打开文档失败: {str(e)}")
            raise ValueError(f"打开文档失败: {str(e)}")

        questions = []
        current_q = None
        pending_questions = []
        has_empty_brackets = False

        # 解析文档段落
        for i, para in enumerate(doc.paragraphs):
            text = para.text.strip()
            if not text:
                continue

            # 题目识别逻辑
            if is_question_line(text, None):
                self.logger.debug(f"[行 {i}] 识别为题目: {text[:50]}...")

                if current_q and current_q.text:
                    questions.append(current_q)
                    self.logger.debug(f"添加上一题: {current_q.text[:30]}..., 答案: {current_q.answer}")

                current_q = Question(text=text)

                # 检查题目行中是否包含答案或空括号
                match = self.answer_pattern.search(text)
                brackets_match = self.empty_brackets_pattern.search(text)

                if match:
                    current_q.answer = match.group(1).upper()
                    self.logger.debug(f"在题目中找到答案: {match.group(1).upper()}")
                    has_empty_brackets = False
                elif brackets_match:
                    self.logger.debug(f"题目包含空括号，等待后续内容中找答案")
                    has_empty_brackets = True
                else:
                    self.logger.debug(f"在题目中未找到答案或空括号")
                    has_empty_brackets = False

            elif self.option_pattern.match(text):
                match = self.option_pattern.match(text)
                option_text = f"{match.group(1)}. {match.group(2).strip()}"
                if current_q:
                    current_q.options.append(option_text)
                    self.logger.debug(f"[行 {i}] 识别为选项: {option_text}")

            # 处理答案和解析
            elif current_q:
                # 检查是否是答案行
                is_answer_line = self._process_answer_line(text, current_q, has_empty_brackets, i)

                if is_answer_line:
                    continue

                # 检查是否是解析行
                if re.match(r'^解析[:：]', text):
                    current_q.explanation = re.sub(r'^解析[:：]\s*', '', text).strip()
                    self.logger.debug(f"[行 {i}] 识别为解析: {text[:50]}...")
                    continue

                # 处理题目延续或新题目
                if not current_q.options and not current_q.explanation:
                    # 检查是否可能是下一题的题目被误认为是上一题的内容
                    if self.question_num_pattern.search(text):
                        self.logger.debug(f"[行 {i}] 可能是新题目，但格式未被识别: {text[:50]}...")

                        # 保存当前题目，如果它没有答案，加入待处理列表
                        if not current_q.answer:
                            self.logger.debug(f"上一题没有答案，加入待处理队列: {current_q.text[:30]}...")
                            pending_questions.append(current_q)
                        else:
                            questions.append(current_q)

                        # 创建新题目
                        current_q = Question(text=text)

                        # 检查题目行中是否包含答案或空括号
                        match = self.answer_pattern.search(text)
                        brackets_match = self.empty_brackets_pattern.search(text)

                        if match:
                            current_q.answer = match.group(1).upper()
                            has_empty_brackets = False
                        elif brackets_match:
                            has_empty_brackets = True
                        else:
                            has_empty_brackets = False
                    else:
                        # 作为题目延续添加
                        current_q.text += '\n' + text
                        self.logger.debug(f"[行 {i}] 添加到题目文本: {text[:50]}...")

        # 处理最后一个题目
        if current_q:
            if current_q.answer:
                questions.append(current_q)
                self.logger.debug(f"添加最后一题: {current_q.text[:30]}..., 答案: {current_q.answer}")
            elif pending_questions:
                # 如果最后一题没有答案，查看是否有待处理题目也没答案
                self.logger.debug(f"最后一题没有答案，检查是否可以从待处理题目中找到匹配")
                pending_questions.append(current_q)

                # 尝试处理没有答案的题目
                for q in pending_questions:
                    # 如果该题包含明显的题号，尝试解析
                    match = re.search(r'^\d+[\.、]|^第(\d+)题', q.text)
                    if match:
                        self.logger.debug(f"处理待定题目: {q.text[:50]}...")

                        # 如果题目有空括号但没答案，尝试从相邻题目中查找答案
                        if self.empty_brackets_pattern.search(q.text) and not q.answer:
                            self._try_find_answer_from_neighbors(q, pending_questions)

                    # 无论如何，添加到问题列表
                    questions.append(q)
            else:
                questions.append(current_q)

        # 清理 pending_questions，确保所有题目都被添加
        for q in pending_questions:
            if q not in questions:
                questions.append(q)
                self.logger.debug(f"添加待处理题目: {q.text[:30]}...")

        # 最终处理：确保所有题目都有答案
        self._finalize_questions(questions)
        self.logger.info(f"解析完成，共解析 {len(questions)} 道题目")
        return questions

    def _process_answer_line(self, text, question, has_empty_brackets, line_num):
        """
        处理可能的答案行

        Args:
            text (str): 文本内容
            question (Question): 题目对象
            has_empty_brackets (bool): 是否有空括号
            line_num (int): 行号

        Returns:
            bool: 是否是答案行
        """
        # 检查是否是答案行
        is_answer_line = False

        # 1. 尝试直接匹配独立答案行
        for pattern in self.separate_answer_patterns:
            match = pattern.search(text)
            if match:
                answer = match.group(1).upper()

                # 如果当前题目有空括号且没有答案，优先填充
                if has_empty_brackets and not question.answer:
                    question.answer = answer
                    self.logger.debug(f"[行 {line_num}] 为题目空括号填充答案: {answer}")
                    has_empty_brackets = False
                else:
                    question.answer = answer
                    self.logger.debug(f"[行 {line_num}] 识别为独立答案行: {text} -> {answer}")

                is_answer_line = True
                break

        # 2. 如果是纯字母行且长度为1，可能是答案
        if not is_answer_line and len(text) == 1 and text.upper() in "ABCD":
            question.answer = text.upper()
            self.logger.debug(f"[行 {line_num}] 识别为单字母答案行: {text}")
            is_answer_line = True

        return is_answer_line

    def _try_find_answer_from_neighbors(self, question, pending_questions):
        """
        尝试从相邻题目找答案

        Args:
            question (Question): 题目对象
            pending_questions (list): 待处理题目列表
        """
        self.logger.debug(f"题目包含空括号但没有关联到答案")

        # 从待处理题目中查找可能的答案
        for other_q in pending_questions:
            if other_q != question and len(other_q.text) == 1 and other_q.text.upper() in "ABCD":
                question.answer = other_q.text.upper()
                self.logger.debug(f"从相邻内容中找到可能的答案: {question.answer}")
                pending_questions.remove(other_q)
                break

    def _finalize_questions(self, questions):
        """
        最终处理所有题目，确保有答案

        Args:
            questions (list): 题目对象列表
        """
        for i, q in enumerate(questions):
            # 1. 先检查题目文本中是否能找到答案
            if not q.answer:
                answer = extract_answer_from_text(q.text, self.separate_answer_patterns)
                if answer:
                    q.answer = answer
                    self.logger.debug(f"从题目文本中提取答案: 题目 {i+1} -> {q.answer}")

            # 2. 如果仍然没答案，尝试从相邻题目推断
            if not q.answer and self.empty_brackets_pattern.search(q.text):
                self._check_next_question_for_answer(questions, i)

    def _check_next_question_for_answer(self, questions, index):
        """
        检查下一题的第一行是否为当前题目的答案

        Args:
            questions (list): 题目对象列表
            index (int): 当前题目索引
        """
        if index < len(questions) - 1:
            next_lines = questions[index+1].text.split('\n')
            if next_lines and len(next_lines[0]) == 1 and next_lines[0].upper() in "ABCD":
                questions[index].answer = next_lines[0].upper()
                self.logger.debug(f"从下一题第一行提取答案: 题目 {index+1} -> {questions[index].answer}")

                # 更新下一题，移除第一行
                if len(next_lines) > 1:
                    questions[index+1].text = '\n'.join(next_lines[1:])