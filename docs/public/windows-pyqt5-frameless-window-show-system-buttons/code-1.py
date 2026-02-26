from ctypes.wintypes import LPRECT, MSG
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import Qt
import win32con


class Window(QWidget):
    def __init__(self, parent = None):
        super().__init__(parent=parent)

    def nativeEvent(self, eventType, message):
        msg = MSG.from_address(int(message))
        if not msg.hWnd:
            return super().nativeEvent(eventType, message)

        if msg.message == win32con.WM_NCCALCSIZE:
            return True, 0
        
        return super().nativeEvent(eventType, message)

if __name__ == '__main__':
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app = QApplication([])
    win = Window()
    win.show()
    app.exec()
