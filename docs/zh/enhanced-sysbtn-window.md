---
description: 此文章是对上一篇文章的补充，修复了对于最大化时窗口上端裁剪的问题，并添加了对窗口深色模式的支持。
head:
  - - meta
    - property: "og:description"
      content: "此文章是对上一篇文章的补充，修复了对于最大化时窗口上端裁剪的问题，并添加了对窗口深色模式的支持。"
---
# [Windows + PyQt5] 修复带有系统按钮窗口的上端裁剪并添加对窗口深色模式的支持

## 简介 {#introduction}

此文章是对[上一篇文章](/zh/windows-pyqt5-frameless-window-show-system-buttons)的补充，[修复了对于最大化时窗口上端裁剪的问题](#fix-maximizing-bug)，并[添加了对窗口深色模式的支持](#add-dark-support)。

## 取消最大化时的窗口上端裁剪 {#fix-maximizing-bug}

[上一篇文章](/zh/windows-pyqt5-frameless-window-show-system-buttons) 中提到，窗口管理器在最大化时，为了避免调整大小，会将窗口四周 `resizeBorderThickness` 大小的区域挤出屏幕，而我们在顶部的这些区域进行了自定义，不想让这些内容被挤出屏幕。更重要的是，我们不能简单的调整客户区大小，因为在最大化时调整客户区顶部位置会使系统按钮停止响应。经过一段时间的探索，我发现了一个**既能**防止顶部挤出屏幕，**又能**保证系统按钮能工作的方法，而这个解决方法主要围绕**一个窗口消息**，和**一个结构体**展开，分别是：

### **[`WM_GETMINMAXINFO`](https://learn.microsoft.com/windows/win32/winmsg/wm-getminmaxinfo) 消息和 [`MINMAXINFO`](https://learn.microsoft.com/windows/win32/api/winuser/ns-winuser-minmaxinfo)** 结构体。 {#strcuctures}

根据 Microsoft 文档，结构体 `MINMAXINFO` 有以下签名：

```cpp
typedef struct tagMINMAXINFO {
  POINT ptReserved;
  POINT ptMaxSize;
  POINT ptMaxPosition;
  POINT ptMinTrackSize;
  POINT ptMaxTrackSize;
} MINMAXINFO, *PMINMAXINFO, *LPMINMAXINFO
```

我们只需要关注两个成员： `ptMaxSize` 和 `ptMaxPosition` ：

- `ptMaxSize` 控制最大化时的宽度和高度；

- `ptMaxPosition` 控制最大化时窗口的坐标。

而这些信息都有默认值供应用程序参考，这些默认值就来自 `WM_GETMINMAXINFO` 消息。

这条消息的值为 0x0024，其参数如下：

> 
> _wParam_
> 
> 未使用此参数。
> 
> _lParam_
> 
> 指向 [`MINMAXINFO`](https://learn.microsoft.com/windows/win32/api/winuser/ns-winuser-minmaxinfo) 结构的指针，该结构包含默认的最大化位置和尺寸，以及默认的最小和最大跟踪大小。 应用程序可以通过设置此结构的成员来替代默认值。

获取这些信息对于 `ctypes` 来说非常简单，关键在于如何设置这些值。

在上一篇文章中，我们使用了 `PyQt5-Frameless-Window` 库以省略一些结构体和实用函数的定义，此库还有一个（对于此文章）非常重要的函数： `getMonitorInfo` ，其位于 `qframelesswindow.utils.win32_utils` 模块中。

`getMonitorInfo` 的实现如下[^1]：

```python
def getMonitorInfo(hWnd, dwFlags):
    """ get monitor info, return `None` if failed

    Parameters
    ----------
    hWnd: int or `sip.voidptr`
        window handle

    dwFlags: int
        Determines the return value if the window does not intersect any display monitor
    """
    monitor = win32api.MonitorFromWindow(hWnd, dwFlags)
    if not monitor:
        return

    return win32api.GetMonitorInfo(monitor)
```

可以看出，这个函数可以获取显示器的大小信息，按照 [`GetMonitorInfo` 的文档](https://learn.microsoft.com/windows/win32/api/winuser/nf-winuser-getmonitorinfow) 和 `getMonitorInfo` 的实现，只需要如此编写即可做出目标的效果：

::: code-group

```python [定义结构体（文件头部）]
from ctypes import Structure
from ctypes.wintypes import POINT, MSG
from qframelesswindow.utils import win32_utils
import win32con
# 其它导入...

class MINMAXINFO(Structure):
    _fields_ = [
        ("ptReserved", POINT),
        ("ptMaxSize", POINT),
        ("ptMaxPosition", POINT),
        ("ptMinTrackSize", POINT),
        ("ptMaxTrackSize", POINT),
    ]
```

```python [在 nativeEvent 中]
	def nativeEvent(self, eventType, message):
        msg = MSG.from_address(int(message))
        if not msg.hWnd:
            return super().nativeEvent(eventType, message)
        # ......
        	return True, lRet.value

        if msg.message == win32con.WM_GETMINMAXINFO:
            mmi = MINMAXINFO.from_address(msg.lParam)
            # 获取当前显示器工作区
            info = win32_utils.getMonitorInfo(msg.hWnd, win32con.MONITOR_DEFAULTTONEAREST)
            work = info['Work']  # (left, top, right, bottom)
            mmi.ptMaxPosition.x = -self.thick
            mmi.ptMaxPosition.y = 0
            mmi.ptMaxSize.x = work[2] - work[0] + self.thick + 1
            mmi.ptMaxSize.y = work[3] - work[1] - 1
            return True, 0
        elif msg.message == win32con.WM_NCHITTEST:
            xPos, yPos = win32gui.ScreenToClient(msg.hWnd, win32api.GetCursorPos())
            clientRect = win32gui.GetClientRect(msg.hWnd)
            w = clientRect[2] - clientRect[0]
            h = clientRect[3] - clientRect[1]
            bw = self.thick
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
		# ...... #
```

:::

效果对比（如果看不清可以点开）：

|                           修复前                           |                          修复后                           |
| :--------------------------------------------------------: | :-------------------------------------------------------: |
| [![修复前的窗口](/enhanced-sysbtn-window/maxfix-before.png)](/enhanced-sysbtn-window/maxfix-before.png) | [![修复后的窗口](/enhanced-sysbtn-window/maxfix-after.png)](/enhanced-sysbtn-window/maxfix-after.png) |

其实这个解决方案有一个不易察觉的**小问题**：为了防止系统判定成最大化，代码里让顶部和底部都留出了 1px 的空隙（放心，顶部的 1px 用户点不到，只能看），就像这样：

| [![顶部的 1px 空隙](/enhanced-sysbtn-window/1px-top.png)](/enhanced-sysbtn-window/1px-top.png) | [![底部的 1px 空隙](/enhanced-sysbtn-window/1px-bottom.png)](/enhanced-sysbtn-window/1px-bottom.png) |
| ------------------------------------------------------------ | ------------------------------------------------------------ |

> :nerd_face:但我个人认为不易察觉的 2px 换引人注目的 8px 还是很值的

## 添加深色模式支持 {#add-dark-support}

从 Windows 10 1903 (内部版本号18362) 开始，Windows 也开始支持深色模式，很多系统应用也添加了对深色模式的支持。在这之中，最引人注目的就是 Windows 资源管理器（以下简称 Explorer）了。毕竟，**这可是个 win32 应用啊！**既然 Explorer 这个 win32 应用都能使用深色模式，别的 win32 应用还有什么不能的呢？

**但是**，微软并没有给出完整的API文档，只提供了[为 Win32 应用程序启用深色模式标题栏](https://learn.microsoft.com/windows/apps/desktop/modernize/ui/apply-windows-themes#enable-a-dark-mode-title-bar-for-win32-applications)的方法。那别的控件（比如系统菜单）怎么办呢？微软并没有给出方法。不过，在社区的讨论[^2][^3]中，我发现了启用“完整”深色模式的方法。

`SetPreferredAppMode` 是一个未文档化、也未按照名称导出的 Windows API 函数，位于 `uxtheme.dll` 的序号 135，用于设置当前进程创建的窗口的颜色模式。它接受一个整数，用于启用或修改深色模式的效果，取值如下：

```cpp
enum PreferredAppMode
{
    Default,
    AllowDark,
    ForceDark,
    ForceLight,
    Max
};
```

> 我们主要关注 `PreferredAppMode` 的三个值：`AllowDark`、`ForceDark`、`ForceLight`。它们分别表示跟随系统主题，强制深色主题，强制浅色主题。[^4]

还有一个重要的函数: `FlushMenuThemes` ，用来在切换主题后更新菜单样式。它同样未文档化、未公开，在 `uxtheme.dll` 中以序号 `136` 进行导出。

那这就简单了啊！我们可以直接继承从 `qframelesswindow` 导出的 [`WindowEffect` 类](https://github.com/zhiyiYo/PyQt-Frameless-Window/blob/master/qframelesswindow/windows/window_effect.py)，并编写辅助函数如下：

```python
from qframelesswindow import WindowEffect
# ...... #

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
```

这样直接在主函数里调用即可：

```python
class Window(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.windowEffect = WindowEffect(self)
        # ...... #
        
        if ...:
            self.windowEffect.setDarkThemeEnabled(self.winId(), True)
            # 别忘了更改标题文本的颜色！
            self.titleBar.setStyleSheet('QLabel{color:white}')
            # 如果使用了 qfluentwidgets ，也别忘记 setTheme 哦！
```

效果如下：

|            |                       激活 + 系统菜单                        |                            未激活                            |
| :--------: | :----------------------------------------------------------: | :----------------------------------------------------------: |
| **窗口化** | [![dark-window-menu.png](/enhanced-sysbtn-window/dark-window-menu.png)](/enhanced-sysbtn-window/dark-window-menu.png) | [![dark-window-inactive.png](/enhanced-sysbtn-window/dark-window-inactive.png)](/enhanced-sysbtn-window/dark-window-inactive.png) |
| **最大化** | [![dark-max-menu.png](/enhanced-sysbtn-window/dark-max-menu.png)](/enhanced-sysbtn-window/dark-max-menu.png) | [![dark-max-inactive.png](/enhanced-sysbtn-window/dark-max-inactive.png)](/enhanced-sysbtn-window/dark-max-inactive.png) |

> :thinking:看起来顶部的 1px 有点明显啊…… 不管了，反正用户都开深色模式了，桌面背景肯定也是深色的:nerd_face:

::: details 从底部裁剪的 1px 点出桌面菜单

[![底部裁剪的 1px 点出桌面菜单](/enhanced-sysbtn-window/dark-max-desktop-menu.png)](/enhanced-sysbtn-window/dark-max-desktop-menu.png)

:::

#### 到目前为止的所有代码可在<a href="/enhanced-sysbtn-window/enhanced-sysbtn-window.py" download="enhanced-sysbtn-window.py">此处</a>下载。 {#download}

<p align="center">--- The END ---</p>

[^1]: https://github.com/zhiyiYo/PyQt-Frameless-Window/blob/master/qframelesswindow/utils/win32_utils.py#L102-L117
[^2]: [windows - Win10 dark theme - how to use in WINAPI? - Stack Overflow](https://stackoverflow.com/questions/53501268/win10-dark-theme-how-to-use-in-winapi)
[^3]: [How to set titlebar context menu to dark theme? · microsoft/WindowsAppSDK · Discussion #2967](https://github.com/microsoft/WindowsAppSDK/discussions/2967)

[^4]: [为 WinUI 3 标题栏原生菜单添加深色主题支持 | Kiyan's Blog](https://kiyanyang.github.io/posts/43fb94d0/)

