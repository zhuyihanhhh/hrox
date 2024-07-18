import sys

from PySide2.QtWidgets import QApplication

from ui.mainWindow import Convert_Window as cw
from ui.mainWindow_function import mainWindow_function as function


def main():
    app = QApplication(sys.argv)
    mainWindow = cw()  # 创建窗口实例
    test = function(mainWindow)  # 创建Test实例，并传入窗口实例
    mainWindow.show()
    sys.exit(app.exec_())


# 调用 main 函数以启动应用程序
if __name__ == '__main__':
    main()
