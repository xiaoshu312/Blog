import ctypes
from ctypes import POINTER # [!code ++]
from ctypes.wintypes import LPRECT, MSG
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import Qt
from qframelesswindow import StandardTitleBar, WindowEffect # [!code ++]
from qframelesswindow.utils import win32_utils 
from qframelesswindow.windows.c_structures import LPNCCALCSIZE_PARAMS, MARGINS
import win32con
import win32gui
import win32api

class Window(QWidget):
    def __init__(self, parent = None):
        super().__init__(parent=parent)
        self.titleBar = StandardTitleBar(self) # [!code ++]
        self.titleBar.minBtn.hide() # [!code ++]
        self.titleBar.maxBtn.hide() # [!code ++]
        self.titleBar.closeBtn.hide() # [!code ++]
        self.windowEffect = WindowEffect(None) # [!code ++]
        self.thick = win32_utils.getResizeBorderThickness(int(self.winId()), False)

        self.DwmDefWindowProc = self.windowEffect.dwmapi.DwmDefWindowProc # [!code ++]
        self.DwmDefWindowProc.argtypes = [ctypes.c_uint, # [!code ++]
            ctypes.c_uint, ctypes.c_uint, ctypes.c_uint, POINTER(ctypes.c_ulong)] # [!code ++]
        self.DwmDefWindowProc.restype = ctypes.c_bool # [!code ++]
        
        self.setStyleSheet('Window{background:transparent;}') # [!code ++]

        self.resize(500, 500) # [!code ++]
        self.updateFrame() 

    def updateFrame(self):
        margins = MARGINS(0, 0, # [!code ++]
            win32_utils.getSystemMetrics(int(self.winId()), 4, True) + self.thick, 0) # [!code ++]
        self.windowEffect.DwmExtendFrameIntoClientArea(int(self.winId()), # [!code ++]
            ctypes.byref(margins)) # [!code ++]
        win32gui.SetWindowPos(int(self.winId()), None, 0, 0, 0, 0, 
            win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_FRAMECHANGED) 

    def resizeEvent(self, e): # [!code ++]
        super().resizeEvent(e) # [!code ++]
        if hasattr(self, 'titleBar'): # [!code ++]
            self.titleBar.resize(e.size().width(), self.titleBar.height()) # [!code ++]

    def nativeEvent(self, eventType, message):
        msg = MSG.from_address(int(message))
        if not msg.hWnd:
            return super().nativeEvent(eventType, message)

        lRet = ctypes.c_ulong() # [!code ++]
        if (hasattr(self, 'DwmDefWindowProc') and # [!code ++]
            self.DwmDefWindowProc(msg.hWnd, # [!code ++]
                                  msg.message, # [!code ++]
                                  msg.wParam, # [!code ++]
                                  msg.lParam, # [!code ++]
                                  ctypes.byref(lRet))): # [!code ++]
            return True, lRet.value # [!code ++]

        if msg.message == win32con.WM_NCHITTEST: 
            xPos, yPos = win32gui.ScreenToClient(msg.hWnd, win32api.GetCursorPos()) 
            clientRect = win32gui.GetClientRect(msg.hWnd) 

            w = clientRect[2] - clientRect[0] 
            h = clientRect[3] - clientRect[1] 

            bw = self.thick 
            lx = xPos < bw  # left 
            rx = xPos > w - bw  # right 
            ty = yPos < bw  # top 
            if lx and ty: 
                return True, win32con.HTTOPLEFT
            elif rx and ty: 
                return True, win32con.HTTOPRIGHT
            elif ty: 
                return True, win32con.HTTOP
            
        elif msg.message == win32con.WM_NCCALCSIZE and hasattr(self, 'thick'): 
            if msg.wParam: 
                rect = ctypes.cast(msg.lParam, LPNCCALCSIZE_PARAMS).contents.rgrc[0] 
            else: 
                rect = ctypes.cast(msg.lParam, LPRECT).contents 

            # rect.top += self.thick
            rect.bottom -= self.thick 

            rect.left += self.thick 
            rect.right -= self.thick 
            return True, 0
        
        elif msg.message == 0x02E0:  # WM_DPICHANGED 
            self.thick = win32_utils.getResizeBorderThickness(int(self.winId()), False) 
            self.updateFrame() 

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
