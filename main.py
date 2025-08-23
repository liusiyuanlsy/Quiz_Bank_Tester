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

import sys
from controllers.app_controller import AppController
from views.app_view import AppView
from utils.logger import get_logger

def main():
    """
    应用程序主入口函数

    初始化应用程序控制器和视图，启动基金考试题库系统。
    处理全局异常并记录日志。
    """
    logger = get_logger()
    logger.info("启动基金考试题库系统")

    try:
        # 创建应用控制器和主视图
        controller = AppController()
        view = AppView(controller)

        # 设置控制器的视图引用
        controller.set_view(view)

        # 启动应用程序
        controller.start()  # 初始化控制器，打开文件选择对话框
        view.start()        # 启动主窗口事件循环
    except Exception as e:
        # 异常捕获和日志记录
        logger.error(f"应用程序运行出错: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())

    logger.info("应用程序退出")

if __name__ == "__main__":
    main()