import sys
from controllers.app_controller import AppController
from views.app_view import AppView
from utils.logger import get_logger

def main():
    """应用程序入口点"""
    logger = get_logger()
    logger.info("启动基金考试题库系统")

    try:
        # 创建控制器和视图
        controller = AppController()
        view = AppView(controller)

        # 设置控制器的视图
        controller.set_view(view)

        # 启动应用程序
        controller.start()
        view.start()
    except Exception as e:
        logger.error(f"应用程序运行出错: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())

    logger.info("应用程序退出")

if __name__ == "__main__":
    main()