import re
from utils.logger import get_logger

logger = get_logger()

def hide_answer_in_text(text):
    """
    隐藏文本中括号内的答案，同时确保保留括号后的内容

    Args:
        text (str): 原始文本

    Returns:
        str: 处理后的文本，答案被隐藏
    """
    # 使用正则表达式一次性替换所有匹配模式的答案
    # 处理多种情况：（A）,(A),（ A）,( A)
    try:
        result = re.sub(r'[（(]\s*[A-Da-d]\s*[）)]', lambda m: m.group(0)[0] + '）' if m.group(0)[0] == '（' else '()', text)

        # 如果文本转换前后长度差异较大，可能存在内容丢失
        if abs(len(text) - len(result)) > 10:
            logger.warning(f"警告：处理前后文本长度差异较大 (原长度: {len(text)}, 新长度: {len(result)})")

        return result
    except Exception as e:
        logger.error(f"隐藏答案时出错: {str(e)}")
        return text

def extract_answer_from_text(text, patterns):
    """
    从文本中提取答案

    Args:
        text (str): 文本内容
        patterns (list): 正则表达式模式列表

    Returns:
        str: 提取的答案，如果没有找到则返回空字符串
    """
    try:
        for pattern in patterns:
            for match in pattern.finditer(text):
                answer = match.group(1).upper()
                logger.debug(f"从文本中提取答案: {answer}")
                return answer
        return ""
    except Exception as e:
        logger.error(f"提取答案时出错: {str(e)}")
        return ""

def is_question_line(text, patterns):
    """
    判断一行文本是否是题目

    Args:
        text (str): 文本内容
        patterns (dict): 正则表达式模式字典

    Returns:
        bool: 是否是题目行
    """
    try:
        return (
            re.match(r'^\（[\u4e00-\u9fa5]+\）\d+[\.、]\s*', text) or
            re.search(r'\)\d+[\.、]\s*$', text) or
            re.match(r'^\d+[\.、]\s*', text) or
            re.match(r'^第\d+题[\.、]?\s*', text) or
            re.match(r'^\d+、.*', text) or
            re.match(r'^\d+[^\d\s].*', text)
        ) and not re.match(r'^解析[:：]', text) and not re.match(r'^答案[:：]', text)
    except Exception as e:
        logger.error(f"判断题目行时出错: {str(e)}")
        return False