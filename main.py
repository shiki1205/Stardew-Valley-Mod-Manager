"""
星露谷 Mod 管理器
主入口文件
"""
import sys
from PyQt6.QtWidgets import QApplication
from frontend.main_window import MainWindow


def main():
    """程序主入口"""
    app = QApplication(sys.argv)
    app.setApplicationName("星露谷 Mod 管理器")
    
    # 创建并显示主窗口
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
