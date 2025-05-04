import os
import re
import random
import time  # 添加time模块导入，用于文件信息显示
import sys  # 添加sys模块导入，用于处理打包后的路径问题
import tkinter as tk
from tkinter import ttk, messagebox
from docx import Document

class QuestionBankApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("基金考试题库系统 — BY Sylvan_930")
        # 调整窗口大小为稍小一点，让所有控件能完整显示
        self.root.geometry("850x650")
        self.configure_styles()

        self.questions = []
        self.current_index = 0
        self.user_answers = {}
        self.random_mode = False

        # 自动搜索题库文件
        bank_files = self.find_question_banks()
        if not bank_files:
            messagebox.showerror("错误", "未找到题库文件！请确保同文件夹下有名称包含'题库'或'题'的Word文档")
            self.root.destroy()
            return

        # 无论找到几个题库文件，都显示选择对话框让用户选择
        print(f"找到 {len(bank_files)} 个题库文件，显示选择对话框")
        bank_file = self._show_file_selection_dialog(bank_files)
        if not bank_file:  # 用户取消了选择
            self.root.destroy()
            return

        try:
            self.load_questions(bank_file)
        except Exception as e:
            messagebox.showerror("错误", f"加载题库失败: {str(e)}")
            self.root.destroy()
            return

        self.create_widgets()
        self.show_question()
        self.root.mainloop()

    def find_question_banks(self):
        """在程序所在目录搜索名称包含'题'的Word文档"""
        bank_files = []
        # 兼容PyInstaller打包后的路径查找
        if getattr(sys, 'frozen', False):
            # 运行于 exe 模式
            search_dir = os.path.dirname(sys.executable)
        else:
            # 运行于脚本模式
            search_dir = os.path.dirname(os.path.abspath(__file__))
        print(f"搜索题库文件，目录: {search_dir}")

        for file in os.listdir(search_dir):
            file_lower = file.lower()
            if file_lower.endswith('.docx') and ('题' in file or file_lower == '题.docx'):
                full_path = os.path.join(search_dir, file)
                file_size = os.path.getsize(full_path) / 1024  # KB
                print(f"找到题库文件: {file} (大小: {file_size:.1f} KB)")
                bank_files.append(file)

        print(f"共找到 {len(bank_files)} 个题库文件")
        return bank_files

    def _show_file_selection_dialog(self, files):
        """显示文件选择对话框，让用户选择题库文件"""
        selection_window = tk.Toplevel(self.root)
        selection_window.title("选择题库文件")
        selection_window.geometry("400x350")
        selection_window.transient(self.root)  # 设置为主窗口的子窗口
        selection_window.grab_set()  # 模态窗口
        selection_window.resizable(False, False)  # 禁止调整大小

        # 说明标签文本根据文件数量调整
        label_text = "找到以下题库文件，请选择要使用的文件："
        if len(files) == 1:
            label_text = "找到一个题库文件，点击确认使用或取消重新选择："

        ttk.Label(
            selection_window,
            text=label_text,
            font=('微软雅黑', 10, 'bold'),
            wraplength=380
        ).pack(pady=(20, 10), padx=20)

        # 创建一个包含列表框和滚动条的容器框架
        list_frame = ttk.Frame(selection_window)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # 创建列表框
        file_listbox = tk.Listbox(
            list_frame,
            font=('微软雅黑', 10),
            height=10,
            selectmode=tk.SINGLE,
            activestyle='dotbox'
        )
        file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 创建滚动条并正确放置
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=file_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        file_listbox.configure(yscrollcommand=scrollbar.set)

        # 添加文件到列表
        for file in files:
            file_listbox.insert(tk.END, file)

            # 获取完整路径和文件信息
            # 兼容PyInstaller打包后的路径查找
            if getattr(sys, 'frozen', False):
                # 运行于 exe 模式
                base_dir = os.path.dirname(sys.executable)
            else:
                # 运行于脚本模式
                base_dir = os.path.dirname(os.path.abspath(__file__))
            full_path = os.path.join(base_dir, file)
            if os.path.exists(full_path):
                file_size = os.path.getsize(full_path) / 1024  # KB
                mod_time = os.path.getmtime(full_path)
                mod_time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(mod_time))
                file_info = f"路径: {full_path}\n大小: {file_size:.1f} KB\n修改时间: {mod_time_str}"
                # 设置提示文本，悬停时显示
                # 注意：Tkinter的Listbox没有直接设置提示的功能，这里只是预留，如需实现可能需要自定义组件

        # 默认选择第一个文件
        if files:
            file_listbox.selection_set(0)
            file_listbox.activate(0)
            file_listbox.see(0)

        # 结果变量
        selected_file = tk.StringVar()

        # 确认按钮回调
        def on_confirm():
            selected_indices = file_listbox.curselection()
            if selected_indices:
                selected_file.set(files[selected_indices[0]])
                selection_window.destroy()

        # 取消按钮回调
        def on_cancel():
            selected_file.set("")
            selection_window.destroy()

        # 双击事件处理
        def on_double_click(event):
            selected_indices = file_listbox.curselection()
            if selected_indices:
                selected_file.set(files[selected_indices[0]])
                selection_window.destroy()

        # 绑定双击事件
        file_listbox.bind('<Double-1>', on_double_click)

        # 按钮区域
        button_frame = ttk.Frame(selection_window)
        button_frame.pack(pady=20)

        confirm_btn = ttk.Button(button_frame, text="确认", command=on_confirm, width=10)
        confirm_btn.pack(side=tk.LEFT, padx=10)
        cancel_btn = ttk.Button(button_frame, text="取消", command=on_cancel, width=10)
        cancel_btn.pack(side=tk.LEFT, padx=10)

        # 设置默认按钮（按回车激活）
        selection_window.bind('<Return>', lambda event: on_confirm())
        selection_window.bind('<Escape>', lambda event: on_cancel())

        # 将焦点设置到列表框
        file_listbox.focus_set()

        # 等待窗口关闭
        self.root.wait_window(selection_window)

        return selected_file.get()

    def configure_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('.', font=('微软雅黑', 10))
        style.configure('TButton', font=('微软雅黑', 10))
        style.configure('TRadiobutton', font=('微软雅黑', 12))
        style.configure('TLabel', font=('微软雅黑', 10))
        style.map('TRadiobutton',
                background=[('selected', '#c1e1c1'), ('!selected', 'white')],
                foreground=[('selected', 'black'), ('!selected', 'black')])

    def create_widgets(self):
        # 题目显示区域 - 缩小高度
        self.txt_question = tk.Text(
            self.root,
            height=6,  # 减小高度以优化布局
            wrap=tk.WORD,
            font=('微软雅黑', 14),
            spacing2=6,
            padx=10,
            pady=10
        )
        self.txt_question.pack(pady=5, padx=20, fill=tk.BOTH, expand=True)

        # 选项区域
        self.var_answer = tk.StringVar()
        self.radios = []
        radio_frame = ttk.Frame(self.root)
        radio_frame.pack(pady=5, fill=tk.X)

        for i in range(4):
            rb = ttk.Radiobutton(
                radio_frame,
                text="",
                variable=self.var_answer,
                value=chr(65+i),
                command=self.update_feedback,
                style='TRadiobutton'
            )
            rb.grid(row=i, column=0, sticky="w", padx=30, pady=3)  # 略微减小间距
            self.radios.append(rb)

        # 反馈区域
        self.feedback_frame = ttk.Frame(self.root)
        self.feedback_frame.pack(pady=5, fill=tk.X, padx=20)

        self.lbl_feedback = ttk.Label(
            self.feedback_frame,
            font=('微软雅黑', 12, 'bold'),
            wraplength=650  # 减小长度以适应新窗口宽度
        )
        self.lbl_feedback.pack(anchor='w')

        self.txt_explanation = tk.Text(
            self.feedback_frame,
            height=4,  # 减小高度
            wrap=tk.WORD,
            font=('微软雅黑', 11),
            state='disabled',
            background='#f5f5f5',
            padx=10,
            pady=5
        )
        self.txt_explanation.pack(fill=tk.X, pady=5)

        # 导航控制区域
        control_frame = ttk.Frame(self.root)
        control_frame.pack(pady=10, fill=tk.X)

        # 上一题/下一题按钮
        nav_frame = ttk.Frame(control_frame)
        nav_frame.pack(side=tk.LEFT, padx=10)
        ttk.Button(
            nav_frame,
            text="上一题",
            command=self.prev_question,
            width=10
        ).grid(row=0, column=0, padx=5)
        ttk.Button(
            nav_frame,
            text="下一题",
            command=self.next_question,
            width=10
        ).grid(row=0, column=1, padx=5)

        # 随机模式复选框
        self.random_var = tk.BooleanVar()
        random_check = ttk.Checkbutton(
            control_frame,
            text="随机抽题",
            variable=self.random_var,
            command=self.toggle_random_mode
        )
        random_check.pack(side=tk.LEFT, padx=10)

        # 跳转题号输入框
        jump_frame = ttk.Frame(control_frame)
        jump_frame.pack(side=tk.RIGHT, padx=10)
        ttk.Label(jump_frame, text="跳转到:").pack(side=tk.LEFT)
        self.jump_entry = ttk.Entry(jump_frame, width=8)
        self.jump_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(
            jump_frame,
            text="跳转",
            command=self.jump_to_question,
            width=6
        ).pack(side=tk.LEFT)

        # 状态栏
        self.lbl_status = ttk.Label(
            self.root,
            text="0/0",
            foreground='#666666'
        )
        self.lbl_status.pack(side=tk.BOTTOM, fill=tk.X, pady=5)

    def load_questions(self, filename):
        doc = Document(filename)
        current_q = {}
        option_pattern = re.compile(r'^([A-D])[\.、:：]?\s*(.*)$')
        answer_pattern = re.compile(r'[（(]\s*([A-Da-d])\s*[）)]')

        # 新增：多种独立答案行格式
        separate_answer_patterns = [
            re.compile(r'^答案[：:]\s*([A-Da-d])', re.IGNORECASE),  # 答案：A
            re.compile(r'^答案[是为]?\s*([A-Da-d])', re.IGNORECASE),  # 答案是A
            re.compile(r'^\s*([A-Da-d])\s*$', re.IGNORECASE),  # 单独的A
            re.compile(r'^[（(]?\s*([A-Da-d])\s*[）)]?$', re.IGNORECASE),  # (A) 或 A
            re.compile(r'.*[（(]\s*([A-Da-d])\s*[）)].*')  # 任何包含(A)的行
        ]

        # 空括号识别模式
        empty_brackets_pattern = re.compile(r'[（(]\s*[）)]')

        print(f"开始解析文件: {filename}")

        # 题目编号提取模式
        question_num_pattern = re.compile(r'^\d+[\.、]|^第\d+题|^\d+、')

        # 题目答案状态跟踪
        pending_questions = []  # 存储暂时没有找到答案的题目
        has_empty_brackets = False  # 当前题目是否有空括号

        for i, para in enumerate(doc.paragraphs):
            text = para.text.strip()
            if not text:
                continue

            # 题目识别逻辑，增加对各种题号格式的支持
            is_question = (
                re.match(r'^\（[\u4e00-\u9fa5]+\）\d+[\.、]\s*', text) or      # (中文)100.格式
                re.search(r'\)\d+[\.、]\s*$', text) or                       # )100.格式
                re.match(r'^\d+[\.、]\s*', text) or                          # 100.格式
                re.match(r'^第\d+题[\.、]?\s*', text) or                      # 第100题格式
                re.match(r'^\d+、.*', text) or                               # 100、格式
                re.match(r'^\d+[^\d\s].*', text)                             # 任何以数字开头后跟非数字非空格
            ) and not re.match(r'^解析[:：]', text) and not re.match(r'^答案[:：]', text)

            if is_question:
                print(f"[行 {i}] 识别为题目: {text[:50]}...")

                if current_q:
                    self.questions.append(current_q)
                    print(f"添加上一题: {current_q['text'][:30]}..., 答案: {current_q['answer']}")

                current_q = {
                    'text': text,
                    'options': [],
                    'answer': '',
                    'explanation': ''
                }

                # 检查题目行中是否包含答案或空括号，但保留完整题目文本
                match = answer_pattern.search(text)
                brackets_match = empty_brackets_pattern.search(text)

                # 保存完整题目文本
                current_q['text'] = text

                if match:
                    # 题目行中直接包含答案，例如"措施包括（A）"
                    current_q['answer'] = match.group(1).upper()
                    print(f"在题目中找到答案: {match.group(1).upper()}")
                    has_empty_brackets = False
                elif brackets_match:
                    # 题目包含空括号，例如"措施包括（）"，需要从后续内容中找答案
                    print(f"题目包含空括号，等待后续内容中找答案")
                    has_empty_brackets = True
                else:
                    print(f"在题目中未找到答案或空括号")
                    has_empty_brackets = False

            elif option_pattern.match(text):
                match = option_pattern.match(text)
                option_text = f"{match.group(1)}. {match.group(2).strip()}"
                if current_q:
                    current_q['options'].append(option_text)
                    print(f"[行 {i}] 识别为选项: {option_text}")

            # 新增：识别多种独立答案行格式
            elif current_q:
                # 检查是否是答案行
                is_answer_line = False

                # 1. 尝试直接匹配独立答案行
                for pattern in separate_answer_patterns:
                    match = pattern.search(text)
                    if match:
                        answer = match.group(1).upper()

                        # 如果当前题目有空括号且没有答案，优先填充
                        if has_empty_brackets and not current_q['answer']:
                            current_q['answer'] = answer
                            print(f"[行 {i}] 为题目空括号填充答案: {answer}")
                            has_empty_brackets = False
                        else:
                            current_q['answer'] = answer
                            print(f"[行 {i}] 识别为独立答案行: {text} -> {answer}")

                        is_answer_line = True
                        break

                # 2. 如果是纯字母行且长度为1，可能是答案
                if not is_answer_line and len(text) == 1 and text.upper() in "ABCD":
                    current_q['answer'] = text.upper()
                    print(f"[行 {i}] 识别为单字母答案行: {text}")
                    is_answer_line = True

                # 3. 如果上一行是题目，但没找到答案，且当前行可能是答案
                if not is_answer_line and len(pending_questions) > 0:
                    for pattern in separate_answer_patterns:
                        match = pattern.search(text)
                        if match:
                            answer = match.group(1).upper()
                            print(f"[行 {i}] 为上一个未解决的题目找到答案: {text} -> {answer}")
                            pending_q = pending_questions.pop()
                            pending_q['answer'] = answer
                            self.questions.append(pending_q)
                            is_answer_line = True
                            break

                if is_answer_line:
                    continue

                # 检查是否是解析行
                if re.match(r'^解析[:：]', text):
                    current_q['explanation'] = re.sub(r'^解析[:：]\s*', '', text).strip()
                    print(f"[行 {i}] 识别为解析: {text[:50]}...")
                    continue

                # 如果既不是选项也不是答案或解析，可能是题目的延续或其他内容
                if not current_q['options'] and not current_q['explanation']:
                    # 检查是否可能是下一题的题目被误认为是上一题的内容
                    # 如果文本以数字开头，可能是新题目
                    if question_num_pattern.search(text):
                        print(f"[行 {i}] 可能是新题目，但格式未被识别: {text[:50]}...")

                        # 保存当前题目，如果它没有答案，加入待处理列表
                        if current_q:
                            if not current_q['answer']:
                                print(f"上一题没有答案，加入待处理队列: {current_q['text'][:30]}...")
                                pending_questions.append(current_q)
                            else:
                                self.questions.append(current_q)

                        # 创建新题目
                        current_q = {
                            'text': text,
                            'options': [],
                            'answer': '',
                            'explanation': ''
                        }

                        # 检查题目行中是否包含答案或空括号
                        # 保存完整题目文本，并检查是否包含答案或空括号
                        current_q['text'] = text
                        match = answer_pattern.search(text)
                        brackets_match = empty_brackets_pattern.search(text)

                        if match:
                            current_q['answer'] = match.group(1).upper()
                            has_empty_brackets = False
                        elif brackets_match:
                            has_empty_brackets = True
                        else:
                            has_empty_brackets = False
                    else:
                        # 作为题目延续添加
                        current_q['text'] += '\n' + text
                        print(f"[行 {i}] 添加到题目文本: {text[:50]}...")

        # 处理最后一个题目
        if current_q:
            if current_q['answer']:
                self.questions.append(current_q)
                print(f"添加最后一题: {current_q['text'][:30]}..., 答案: {current_q['answer']}")
            elif len(pending_questions) > 0:
                # 如果最后一题没有答案，查看是否有待处理题目也没答案
                print(f"最后一题没有答案，检查是否可以从待处理题目中找到匹配")
                pending_questions.append(current_q)

                # 尝试处理没有答案的题目
                for q in pending_questions:
                    # 如果该题包含明显的题号，尝试解析
                    # 优化：使用更简明的题号匹配逻辑
                    match = re.search(r'^\d+[\.、]|^第(\d+)题', q['text'])
                    if match:
                        print(f"处理待定题目: {q['text'][:50]}...")

                        # 如果题目有空括号但没答案，尝试从相邻题目中查找答案
                        if empty_brackets_pattern.search(q['text']) and not q['answer']:
                            self._try_find_answer_from_neighbors(q, pending_questions)

                    # 无论如何，添加到问题列表
                    self.questions.append(q)
            else:
                self.questions.append(current_q)

        # 清理 pending_questions，确保所有题目都被添加
        for q in pending_questions:
            if q not in self.questions:
                self.questions.append(q)
                print(f"添加待处理题目: {q['text'][:30]}...")

        # 最终处理：确保所有题目都有答案
        self._finalize_questions(separate_answer_patterns, empty_brackets_pattern)
        print(f"解析完成，共解析 {len(self.questions)} 道题目")

    def _try_find_answer_from_neighbors(self, question, pending_questions):
        """尝试从相邻题目找答案"""
        print(f"题目包含空括号但没有关联到答案")

        # 从待处理题目中查找可能的答案
        for other_q in pending_questions:
            if other_q != question and len(other_q['text']) == 1 and other_q['text'].upper() in "ABCD":
                question['answer'] = other_q['text'].upper()
                print(f"从相邻内容中找到可能的答案: {question['answer']}")
                pending_questions.remove(other_q)
                break

    def _finalize_questions(self, separate_answer_patterns, empty_brackets_pattern):
        """最终处理所有题目，确保有答案"""
        for i, q in enumerate(self.questions):
            # 1. 先检查题目文本中是否能找到答案
            if not q['answer']:
                self._extract_answer_from_text(q, i, separate_answer_patterns)

            # 2. 如果仍然没答案，尝试从相邻题目推断
            if not q['answer'] and empty_brackets_pattern.search(q['text']):
                self._check_next_question_for_answer(i)

    def _extract_answer_from_text(self, question, index, patterns):
        """从题目文本中提取答案 - 优化版"""
        # 一次性在整个文本中查找
        for pattern in patterns:
            for match in pattern.finditer(question['text']):
                question['answer'] = match.group(1).upper()
                print(f"从题目文本中提取答案: 题目 {index+1} -> {question['answer']}")
                return

    def _check_next_question_for_answer(self, index):
        """检查下一题的第一行是否为当前题目的答案"""
        if index < len(self.questions) - 1:
            next_lines = self.questions[index+1]['text'].split('\n')
            if next_lines and len(next_lines[0]) == 1 and next_lines[0].upper() in "ABCD":
                self.questions[index]['answer'] = next_lines[0].upper()
                print(f"从下一题第一行提取答案: 题目 {index+1} -> {self.questions[index]['answer']}")

                # 更新下一题，移除第一行
                if len(next_lines) > 1:
                    self.questions[index+1]['text'] = '\n'.join(next_lines[1:])

    def _hide_answer_in_text(self, text):
        """隐藏文本中括号内的答案，同时确保保留括号后的内容"""
        # 使用正则表达式一次性替换所有匹配模式的答案
        import re
        # 处理多种情况：（A）,(A),（ A）,( A)
        result = re.sub(r'[（(]\s*[A-Da-d]\s*[）)]', lambda m: m.group(0)[0] + '）' if m.group(0)[0] == '（' else '()', text)

        # 如果文本转换前后长度差异较大，可能存在内容丢失
        if abs(len(text) - len(result)) > 10:
            print(f"警告：处理前后文本长度差异较大 (原长度: {len(text)}, 新长度: {len(result)})")

        return result

    # 移除了此处的create_widgets重复方法

    def show_question(self):
        """显示当前题目，并隐藏题目中的答案"""
        if not self.questions:
            return

        self.reset_feedback()
        self.var_answer.set("")  # 重置选项状态
        self.lbl_status.config(text=f"第 {self.current_index+1}/{len(self.questions)} 题")
        q = self.questions[self.current_index]

        # 隐藏答案
        orig_text = q['text']
        # 使用优化后的方法处理答案
        display_text = self._hide_answer_in_text(orig_text)

        # 清空并设置文本框内容
        self.txt_question.config(state='normal')
        self.txt_question.delete(1.0, tk.END)
        self.txt_question.insert(tk.END, display_text)

        # 设置选项
        for i, radio in enumerate(self.radios):
            if i < len(q['options']):
                radio.config(text=q['options'][i], state='normal')
            else:
                radio.config(text="", state='disabled')

        self.txt_question.config(state='disabled')

    def reset_feedback(self):
        self.lbl_feedback.config(text="")
        self.txt_explanation.config(state='normal')
        self.txt_explanation.delete(1.0, tk.END)
        self.txt_explanation.config(state='disabled')

    def update_feedback(self):
        # 先重置反馈区域
        self.reset_feedback()

        user_answer = self.var_answer.get()
        if not user_answer:
            return

        q = self.questions[self.current_index]

        if user_answer == q['answer']:
            self.lbl_feedback.config(
                text=f"✅ 回答正确！正确答案是：{q['answer']}",
                foreground="green"
            )
        else:
            self.lbl_feedback.config(
                text=f"❌ 回答错误！您的选择：{user_answer}，正确答案：{q['answer']}",
                foreground="red"
            )

        if q['explanation']:
            self.txt_explanation.config(state='normal')
            self.txt_explanation.insert(tk.END, "【题目解析】\n" + q['explanation'])
            self.txt_explanation.config(state='disabled')

    def prev_question(self):
        if self.random_mode:
            self.current_index = random.randint(0, len(self.questions)-1)
        elif self.current_index > 0:
            self.current_index -= 1
        self.show_question()

    def next_question(self):
        if self.random_mode:
            self.current_index = random.randint(0, len(self.questions)-1)
        elif self.current_index < len(self.questions)-1:
            self.current_index += 1
        self.show_question()

    def toggle_random_mode(self):
        self.random_mode = self.random_var.get()

    def jump_to_question(self):
        try:
            question_num = int(self.jump_entry.get())
            if 1 <= question_num <= len(self.questions):
                self.current_index = question_num - 1
                self.show_question()
            else:
                messagebox.showerror("错误", f"请输入1-{len(self.questions)}之间的题号")
        except ValueError:
            messagebox.showerror("错误", "请输入有效的题号数字")

if __name__ == "__main__":
    QuestionBankApp()