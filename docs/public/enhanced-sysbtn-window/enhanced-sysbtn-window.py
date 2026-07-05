import ctypes
import pywintypes
from ctypes import POINTER, Structure, c_long, wintypes, WinError, CFUNCTYPE, cast
from ctypes.wintypes import LPRECT, MSG, POINT
from PyQt5.QtWidgets import QApplication, QWidget, QLabel
from PyQt5.QtCore import Qt, QEvent, QTimer
from qframelesswindow import StandardTitleBar, WindowEffect
from qframelesswindow.utils import win32_utils
from qframelesswindow.windows.c_structures import LPNCCALCSIZE_PARAMS, MARGINS, DWM_BLURBEHIND
import win32con
import win32gui
import win32api

class MINMAXINFO(Structure):
    _fields_ = [
        ("ptReserved", POINT),
        ("ptMaxSize", POINT),
        ("ptMaxPosition", POINT),
        ("ptMinTrackSize", POINT),
        ("ptMaxTrackSize", POINT),
    ]

class WindowEffect(WindowEffect):
    def __init__(self, window):
        super().__init__(window)
        self.uxtheme = ctypes.WinDLL('uxtheme.dll')
        self.SetPreferredAppMode = self.uxtheme[135]
        self.SetPreferredAppMode.argtypes = [ctypes.c_int]
        self.SetPreferredAppMode.restype = ctypes.c_int

        self.FlushMenuThemes = self.uxtheme[136]
        
    def setDarkThemeEnabled(self, hWnd, isDarkTheme):
        # enable dark/light title bar
        self.DwmSetWindowAttribute(
            int(hWnd),
            20,  # DWMWA_USE_IMMERSIVE_DARK_MODE
            ctypes.byref(ctypes.c_int(isDarkTheme)),
            4  # sizeof(c_bool)
        )

        # enable dark/light win32 menus
        self.SetPreferredAppMode(2 if isDarkTheme else 3)
        self.FlushMenuThemes()
        
class Window(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.titleBar = StandardTitleBar(self)
        self.titleBar.minBtn.hide()
        self.titleBar.maxBtn.hide()
        self.titleBar.closeBtn.hide()
        self.windowEffect = WindowEffect(self)
        self._resizeBorderThickness = win32_utils.getResizeBorderThickness(int(self.winId()), False)

        self.DwmDefWindowProc = self.windowEffect.dwmapi.DwmDefWindowProc
        self.DwmDefWindowProc.argtypes = [ctypes.c_uint,
            ctypes.c_uint, ctypes.c_uint, ctypes.c_uint, POINTER(ctypes.c_ulong)]
        self.DwmDefWindowProc.restype = ctypes.c_bool

        self.setStyleSheet('Window{background:transparent;}')

        self.resize(500, 500)
        self.updateFrame()

        # If you don't want to enable dark mode, just comment the
        # two lines of code below.
        self.windowEffect.setDarkThemeEnabled(self.winId(), True)
        self.titleBar.setStyleSheet('QLabel{color:white}')

    def updateFrame(self):
        margins = MARGINS(0, 0,
            win32_utils.getSystemMetrics(int(self.winId()), 4, True) + self._resizeBorderThickness, 0)
        self.windowEffect.DwmExtendFrameIntoClientArea(int(self.winId()),
            ctypes.byref(margins))
        win32gui.SetWindowPos(int(self.winId()), None, 0, 0, 0, 0,
            win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_FRAMECHANGED)

    def resizeEvent(self, e):
        super().resizeEvent(e)
        if hasattr(self, 'titleBar'):
            self.titleBar.resize(e.size().width(), self.titleBar.height())

    def nativeEvent(self, eventType, message):
        msg = MSG.from_address(int(message))
        if not msg.hWnd:
            return super().nativeEvent(eventType, message)

        lRet = ctypes.c_ulong()
        if (hasattr(self, 'DwmDefWindowProc') and
            self.DwmDefWindowProc(msg.hWnd,
                                  msg.message,
                                  msg.wParam,
                                  msg.lParam,
                                  ctypes.byref(lRet))):
            return True, lRet.value

        if msg.message == win32con.WM_GETMINMAXINFO:
            mmi = MINMAXINFO.from_address(msg.lParam)
            info = win32_utils.getMonitorInfo(msg.hWnd, win32con.MONITOR_DEFAULTTONEAREST)
            work = info['Work']  # (left, top, right, bottom)
            mmi.ptMaxPosition.x = -self._resizeBorderThickness
            mmi.ptMaxPosition.y = 0
            mmi.ptMaxSize.x = work[2] - work[0] + self._resizeBorderThickness + 1
            mmi.ptMaxSize.y = work[3] - work[1] - 1
            return True, 0
        elif msg.message == win32con.WM_NCHITTEST:
            xPos, yPos = win32gui.ScreenToClient(msg.hWnd, win32api.GetCursorPos())
            clientRect = win32gui.GetClientRect(msg.hWnd)
            w = clientRect[2] - clientRect[0]
            h = clientRect[3] - clientRect[1]
            bw = self._resizeBorderThickness
            lx = xPos < bw
            rx = xPos > w - bw
            ty = yPos < bw
            if not win32_utils.isMaximized(msg.hWnd):
                if lx and ty:
                    return True, win32con.HTTOPLEFT
                elif rx and ty:
                    return True, win32con.HTTOPRIGHT
                elif ty:
                    return True, win32con.HTTOP
            if hasattr(self, 'titleBar'):
                tbh = self.titleBar.height()
                tbw = self.titleBar.width()
                tbx = self.titleBar.x()
                tby = self.titleBar.y()
                if tbx <= xPos <= tbx+tbw and 0 <= yPos <= tby+tbh:
                    if (hasattr(self.titleBar, 'iconLabel') and
                        self.childAt(xPos, yPos) == self.titleBar.iconLabel):
                        return True, win32con.HTSYSMENU
                    return True, win32con.HTCAPTION

        elif msg.message == win32con.WM_NCCALCSIZE and hasattr(self, '_resizeBorderThickness'):
            if msg.wParam:
                rect = ctypes.cast(msg.lParam, LPNCCALCSIZE_PARAMS).contents.rgrc[0]
            else:
                rect = ctypes.cast(msg.lParam, LPRECT).contents

            isMaximized = win32_utils.isMaximized(msg.hWnd)
            rect.bottom -= 0 if isMaximized else self._resizeBorderThickness
            rect.left += self._resizeBorderThickness
            rect.right -= 1 if isMaximized else self._resizeBorderThickness
            return True, 0

        elif msg.message == 0x02E0:  # WM_DPICHANGED
            self._resizeBorderThickness = win32_utils.getResizeBorderThickness(int(self.winId()), False)
            self.updateFrame()

        return super().nativeEvent(eventType, message)

if __name__ == '__main__':
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app = QApplication([])
    win = Window()
    win.setWindowTitle('Title')
    win.show()
    app.exec()

