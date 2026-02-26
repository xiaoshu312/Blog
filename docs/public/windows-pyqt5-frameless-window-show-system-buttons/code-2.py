import ctypes # [!code ++]
from ctypes.wintypes import MSG # [!code --]
from ctypes.wintypes import LPRECT, MSG # [!code ++]
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import Qt
from qframelesswindow.utils import win32_utils # [!code ++]
from qframelesswindow.windows.c_structures import LPNCCALCSIZE_PARAMS # [!code ++]
import win32con
import win32gui # [!code ++]
import win32api # [!code ++]

class Window(QWidget):
    def __init__(self, parent = None):
        super().__init__(parent=parent)
        self.thick = win32_utils.getResizeBorderThickness(int(self.winId()), False) # [!code ++]

        self.updateFrame() # [!code ++]

    def updateFrame(self): # [!code ++]
        win32gui.SetWindowPos(int(self.winId()), None, 0, 0, 0, 0, # [!code ++]
            win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_FRAMECHANGED) # [!code ++]

    def nativeEvent(self, eventType, message):
        msg = MSG.from_address(int(message))
        if not msg.hWnd:
            return super().nativeEvent(eventType, message)

        if msg.message == win32con.WM_NCHITTEST: # [!code ++]
            xPos, yPos = win32gui.ScreenToClient(msg.hWnd, win32api.GetCursorPos()) # [!code ++]
            clientRect = win32gui.GetClientRect(msg.hWnd) # [!code ++]

            w = clientRect[2] - clientRect[0] # [!code ++]
            h = clientRect[3] - clientRect[1] # [!code ++]

            bw = self.thick # [!code ++]
            lx = xPos < bw  # left # [!code ++]
            rx = xPos > w - bw  # right # [!code ++]
            ty = yPos < bw  # top # [!code ++]
            if lx and ty: # [!code ++]
                return True, win32con.HTTOPLEFT # [!code ++]
            elif rx and ty: # [!code ++]
                return True, win32con.HTTOPRIGHT # [!code ++]
            elif ty: # [!code ++]
                return True, win32con.HTTOP # [!code ++]
            
        if msg.message == win32con.WM_NCCALCSIZE: # [!code --]
        elif msg.message == win32con.WM_NCCALCSIZE and hasattr(self, 'thick'): # [!code ++]
            if msg.wParam: # [!code ++]
                rect = ctypes.cast(msg.lParam, LPNCCALCSIZE_PARAMS).contents.rgrc[0] # [!code ++]
            else: # [!code ++]
                rect = ctypes.cast(msg.lParam, LPRECT).contents # [!code ++]

            # rect.top += self.thick
            rect.bottom -= self.thick # [!code ++]

            rect.left += self.thick # [!code ++]
            rect.right -= self.thick # [!code ++]
            return True, 0
        
        elif msg.message == 0x02E0:  # WM_DPICHANGED # [!code ++]
            self.thick = win32_utils.getResizeBorderThickness(int(self.winId()), False) # [!code ++]
            self.updateFrame() # [!code ++]

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
