# 基金考试题库系统

## 项目介绍
这是一个简单而实用的题库测试系统，专为基金从业资格考试等类似考试设计。系统支持多种文件格式的题库导入，可以进行随机抽题、答案记录和成绩统计。

## 软件架构
本项目采用MVC（Model-View-Controller）架构模式设计：
- **Model**：处理数据和业务逻辑
  - `models/question.py`：题目模型
  - `models/question_bank.py`：题库管理模型
- **View**：用户界面相关
  - `views/app_view.py`：主应用视图
  - `views/components/`：UI组件（题目、反馈、导航等）
- **Controller**：控制程序流程
  - `controllers/app_controller.py`：主控制器
- **Services**：提供特定功能服务
  - `services/file_service.py`：文件操作服务
  - `services/parser_service.py`：文件解析服务
- **Utils**：工具类
  - `utils/logger.py`：日志工具
  - `utils/text_utils.py`：文本处理工具

## 安装教程

1. 克隆或下载本仓库到本地
```
git clone [仓库地址] [项目路径]
```

2. 使用uv（或pip）安装依赖
```
cd [项目路径]
uv init .
uv add python-docx lxml Pillow
```
或使用pip
```
pip install python-docx lxml Pillow
```

3. 直接运行
```
python main.py
```

4. 打包为可执行文件的详细说明

### 打包准备工作
首先，确保已安装PyInstaller：
```
pip install pyinstaller
```

### 完整打包流程
以下是在不同操作系统上打包的详细步骤：

#### Windows系统打包
```
# 进入项目目录
cd [项目路径]

# 基本打包命令
pyinstaller --onefile --windowed --name="基金考试题库系统" main.py

# 高级打包命令（推荐）
pyinstaller --onefile --windowed --name="基金考试题库系统" --icon=resources/icon.ico --clean --hidden-import=docx --hidden-import=tkinter --hidden-import=lxml --hidden-import=PIL main.py
```

#### macOS系统打包
```
# 进入项目目录
cd [项目路径]

# 打包命令
pyinstaller --onefile --windowed --name="基金考试题库系统" --icon=resources/icon.icns main.py
```

#### Linux系统打包
```
# 进入项目目录
cd [项目路径]

# 打包命令
pyinstaller --onefile --windowed --name="基金考试题库系统" main.py
```

### 打包参数说明
- `--onefile`：将所有依赖打包成单个可执行文件
- `--windowed`：以窗口模式运行，不显示控制台窗口
- `--name`：指定输出的可执行文件名称
- `--icon`：指定应用程序图标（.ico、.icns等格式）
- `--clean`：清理临时文件
- `--hidden-import`：指定额外导入的模块，解决可能的导入错误

### 打包输出位置
打包完成后，可执行文件在以下位置：
- Windows: `[项目路径]/dist/基金考试题库系统.exe`
- macOS: `[项目路径]/dist/基金考试题库系统.app`
- Linux: `[项目路径]/dist/基金考试题库系统`

### 常见问题与解决方案
1. **缺少模块错误**：如遇到ImportError，在打包命令中添加`--hidden-import=模块名`
2. **字体/资源文件缺失**：添加`--add-data="资源目录;目标目录"`参数
3. **打包文件过大**：使用`--exclude-module=不需要的模块`排除不必要的库
4. **无法正常启动**：尝试使用`--debug=all`参数获取详细日志进行排查

### 发布与分发
打包完成后，您可以：
1. 直接分发exe文件（Windows）或app文件（macOS）
2. 创建安装程序（可使用NSIS等工具）
3. 将可执行文件与README、LICENSE等文档一起打包为zip文件分发

## 功能特点

- **文件选择**：使用系统文件选择器直接选择任意题库文件
- **多格式支持**：支持解析 `.docx`、`.txt` 和 `.csv` 等多种格式的题库文件
- **智能解析**：自动识别题目、选项和答案
- **随机抽题**：支持顺序或随机模式答题
- **答题记录**：可选择是否保存答题记录
- **成绩统计**：提供已答题数、正确率等实时统计
- **题目跳转**：支持直接跳转到指定题号

## 使用说明

1. 启动程序后，系统会弹出文件选择对话框，选择您的题库文件
2. 题库加载成功后，显示第一道题目，开始答题
3. 点击选项选择答案，系统会即时给出正确答案和解析
4. 使用"上一题"、"下一题"按钮或跳转功能浏览题目
5. 可选择"随机抽题"和"保存做题记录"等设置
6. 使用右下角"重新选取题库"按钮可随时切换不同的题库文件

## 题库文件格式要求

系统支持以下格式的题库文件：
- Word文档(.docx)
- 文本文件(.txt)
- CSV文件(.csv)
- 其他文本格式文件

题库文件内容需满足一定的格式要求，例如：
```
1. 这是一道单选题？
A. 选项A
B. 选项B
C. 选项C
D. 选项D
答案：A
解析：这是解析内容

2. 这是第二道题...
```

## 最近更新

- 简化了程序结构，删除了题库选择器部分
- 使用系统文件选择器直接打开任意类型文件
- 优化了题目跳转功能，跳转后自动清空输入框
- 改进了文件解析和错误处理逻辑

## 许可证

请查看项目中的LICENSE文件
