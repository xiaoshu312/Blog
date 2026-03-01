# [Windows] Displaying System Buttons in a PyQt5 Frameless Window

## Introduction {#Introduction}

When using many software applications on Windows, we sometimes notice that some windows look a bit unusual, like these:

![Microsoft Word 2007 with custom frame](/windows-pyqt5-frameless-window-show-system-buttons/word2007-customframe.png)

![Windows 10 Explorer with custom frame](/windows-pyqt5-frameless-window-show-system-buttons/explorer10-customframe.png)

As we all know, under normal circumstances, the content on the window borders is managed by the operating system, and applications cannot interfere with it. However, these windows manage to place their own controls on the title bar while retaining the system's (native) title bar buttons. How is this achieved?

> [!TIP]
>
> The Python version used in this article is 3.11.9 or 3.8.10 (on Win7), PyQt5 version is 5.15.9, and the code has been tested on Windows 7 (6.1), Windows 10 (10.0.19045), and Windows 11 (10.0.22621 and above).
>
> In theory, any Windows Vista or later system capable of running PyQt5, PyWin32, and ctypes can use this method.

<p align="center">--- The main content begins ---</p>

## 1. First, we need a frameless window {#First}

Let's look at the code:

<<< @/public/windows-pyqt5-frameless-window-show-system-buttons/code-1.py{16,17}

This "frameless" window might be slightly different from the code you usually use. It does not modify `windowFlags`. Instead, it removes the standard window frame by handling the `WM_NCCALCSIZE` message in `nativeEvent`, turning the window into a "frameless window" while retaining its original `windowFlags`.

The effect is as follows:

![An empty frameless window, no border, no title bar, no shadow](/windows-pyqt5-frameless-window-show-system-buttons/code-1.png)

The difference from using the ordinary `Qt.FramelessWindowHint` is that this window still has a system menu (try pressing `Alt`+`Space`), and it can be maximized and minimized.

## 2. Adding window shadows {#Second}

Again, let's start with the code:

<<< @/public/windows-pyqt5-frameless-window-show-system-buttons/code-2.py

> [!IMPORTANT]
>
> This code uses a window library called [`PyQt5-Frameless-Window`](https://github.com/zhiyiYo/PyQt-Frameless-Window). This library encapsulates a cross-platform frameless window. In this article, I only use the C structures, some utility functions, and other bits from this library's implementation details, not the library's window part itself.

Let's first look at `nativeEvent`. In the part handling `WM_NCCALCSIZE` (lines 29~38), I added some calculations. These calculations can modify the margins of the window's non-client area (NCA), making the resizing borders behave identically to the borders of a standard framed window (essentially, the left, bottom, and right borders are handed over to the standard window frame, thus providing shadows and the same resizing behavior as a "window with borders").

At this point, observant readers might wonder:

> Why not adjust the top border margin as well?

Well, you cannot adjust **all** four borders; otherwise, strange things happen. You can try it yourself, haha.

Next is `WM_NCHITTEST`: This compensates for not adjusting the top border — with this handling, the top border can also be used for resizing.

Now, let's look at `WM_DPICHANGED` below (the constant for this is not available in the `win32con` I'm using). This handling is primarily to match the new DPI's `resizeBorderThickness` when the DPI changes, adjusting the window margins to the new size.

Now, look at `updateFrame`. This is important: without this, the window might not become a frameless window until you manually resize it after it appears. The purpose of this function is to automatically refresh the frame.

Alright, let's see the effect:

![An empty frameless window, now with shadows, and resizable on all four sides](/windows-pyqt5-frameless-window-show-system-buttons/code-2.png)

Now that we have shadows and can resize, it's time to get back to the main topic:

## 3. Custom Title Bar + System Buttons {#Third}

As usual, let's see the code first:

<<< @/public/windows-pyqt5-frameless-window-show-system-buttons/code-3.py

And the effect:

![A window with a title bar, but no icon or title on the title bar, yet it has system buttons. The content area below is black, and the window border is white.](/windows-pyqt5-frameless-window-show-system-buttons/code-3.png)

Look at `__init__`. It adds `titleBar`, which is the standard title bar from `PyQt5-Frameless-Window`, containing a window icon, title, and three buttons. In this example, we have system buttons, so we don't need the buttons provided by the title bar; we hide them.

In `__init__`, there's also [`DwmDefWindowProc`](https://learn.microsoft.com/windows/win32/api/dwmapi/nf-dwmapi-dwmdefwindowproc), a crucial Windows API function exported by dwmapi.dll. We declare its parameter and return types here; we'll discuss its purpose shortly.

Next is a call to `setStyleSheet` to clear the theme's default background. Due to DWM's characteristics, system buttons are at the bottom of the window's Z-order for controls (below the background), so controls or backgrounds would obscure the system buttons.

Then we resize the window because adding controls would otherwise make the window very small (due to the initial size of `StandardTitleBar`).

In the `updateFrame` method, the call to [`DwmExtendFrameIntoClientArea`](https://learn.microsoft.com/windows/win32/api/dwmapi/nf-dwmapi-dwmextendframeintoclientarea) extends the standard title bar area down into the client area by a standard title bar height (note: this is not hardcoded as 32px; it's obtained from the [`GetSystemMetrics`](https://learn.microsoft.com/windows/win32/api/winuser/nf-winuser-getsystemmetrics) function for the title bar height plus the resizing border thickness). Within this extended area, the system provides the system buttons. Hence, this is the most crucial part.

Then, the code in the `resizeEvent` handler simply adjusts the title bar widget to match the window's width.

Now we enter the **most important** part: `nativeEvent`! Here, we call the [`DwmDefWindowProc`](https://learn.microsoft.com/windows/win32/api/dwmapi/nf-dwmapi-dwmdefwindowproc) function. Its role is to respond to interactions with the system buttons, such as hover, click, leave, etc. Without this, the system buttons would be mere decorations that do nothing.

Some details need clarification:

1.  As you may have noticed, similar to Windows Explorer, the window border becomes white. This issue only occurs on Windows 10; other versions do not exhibit this:
    - When the values in the [`MARGINS`](https://learn.microsoft.com/windows/win32/api/uxtheme/ns-uxtheme-margins) structure passed to [`DwmExtendFrameIntoClientArea`](https://learn.microsoft.com/windows/win32/api/dwmapi/nf-dwmapi-dwmextendframeintoclientarea) are all natural numbers, the window border is white.
    - When the values in the [`MARGINS`](https://learn.microsoft.com/windows/win32/api/uxtheme/ns-uxtheme-margins) structure passed to [`DwmExtendFrameIntoClientArea`](https://learn.microsoft.com/windows/win32/api/dwmapi/nf-dwmapi-dwmextendframeintoclientarea) include negative numbers, the window border… doesn't show at all!
    - When the values in the [`MARGINS`](https://learn.microsoft.com/windows/win32/api/uxtheme/ns-uxtheme-margins) structure passed to [`DwmExtendFrameIntoClientArea`](https://learn.microsoft.com/windows/win32/api/dwmapi/nf-dwmapi-dwmextendframeintoclientarea) are all 0 (i.e., the default), the window border is the normal dark gray (might vary with theme mode).

2.  When maximized, the window's "title bar" area will have a portion equal to `resizeBorderThickness` pushed off the screen. This is likely to prevent the user from resizing the window when maximized, but… this operation is quite odd! Why not just disable resizing directly, why move the resizable area off-screen? But since Microsoft has set this _rule_, we can't change it. To prevent the controls on the title bar from not being vertically centered, you can adjust the title bar's height, move all window controls, or adjust the layout's `contentsMargins` (if available).

    > Actually, there is another simple method. You could check if the window is maximized when handling `WM_NCCALCSIZE` and then adjust the top margin accordingly (when maximized, adjusting all four margins is possible without causing strange behavior), adding a `resizeBorderThickness` to it. This achieves the effect without modifying window properties. Unfortunately, this approach is not friendly to windows containing system buttons, because adjusting the top margin when maximized causes the system buttons to stop responding again (possibly a bug), so other methods must be tried.

With the above, you now have a window that includes system buttons, and these buttons automatically switch styles according to the theme settings. Go ahead and use it!

## Remarks {#Remarks}

1.  The window with system buttons implemented via the above method is not perfect because it does not support opening the [system menu](https://learn.microsoft.com/windows/win32/menurc/about-menus#the-window-menu) by clicking the window icon or right-clicking the title bar. I have implemented a version that includes the system menu [here](https://gist.github.com/xiaoshu312/291999ae2c726b966ca2d2bc4b9a810d), but it still has some issues. Feel free to take a look!

2.  Regarding the maximization issue, Chromium seems to have a good workaround, but I haven't investigated it yet.

    > [!TIP]
    >
    > Did you know? On Windows 11, starting Chromium with the `--enable-features=Windows11MicaTitlebar` parameter can launch Chromium with system buttons!
    >
    > [![Microsoft Edge with system buttons](/windows-pyqt5-frameless-window-show-system-buttons/microsoft-edge-mica-windows-11-hero.webp)](https://pureinfotech.com/microsoft-edge-mica-material-windows-11/)
    >
    > Note: Microsoft Edge in the image is also based on the Chromium kernel. (I probably don't need to say this)

3.  On Windows 11, the window above may not have the Mica effect. To enable it, simply add the following at the end of `__init__`:

    ```python
    if win32_utils.isGreaterEqualWin11():
        self.windowEffect.setMicaEffect(self.winId())
    ```

    Then you can see the Mica effect on the title bar. For more information about `WindowEffect`, see [window_effect.py](https://github.com/zhiyiYo/PyQt-Frameless-Window/blob/master/qframelesswindow/windows/window_effect.py).

## References {#References}

1.  [Custom Window Frame Using DWM - Microsoft Learn](https://learn.microsoft.com/windows/win32/dwm/customframe)
2.  [c++ - Why is my DwmExtendFrameIntoClientArea()'d window not drawing the DWM borders? - Stack Overflow](https://stackoverflow.com/questions/41106347/why-is-my-dwmextendframeintoclientaread-window-not-drawing-the-dwm-borders)
3.  [zhiyiYo/PyQt-Frameless-Window: A cross-platform frameless window based on PyQt/PySide, support Win32, Linux and macOS.](https://github.com/zhiyiYo/PyQt-Frameless-Window)