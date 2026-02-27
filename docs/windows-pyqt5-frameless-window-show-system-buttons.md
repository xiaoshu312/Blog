# [Windows] Display System Buttons in a PyQt5 Frameless Window

## Introduction

When using many software applications on Windows, we sometimes notice that some windows look a bit unusual, like these:

![Microsoft Word 2007 custom frame](/windows-pyqt5-frameless-window-show-system-buttons/word2007-customframe.png)

![Windows 10 Explorer custom frame](/windows-pyqt5-frameless-window-show-system-buttons/explorer10-customframe.png)

As we know, (normally) the content on the window border is managed by the operating system and is inaccessible to applications. However, these windows can place their own controls on the title bar while retaining the system-provided (native) title bar buttons. How is this achieved?

> [!TIP]
>
> The Python version used in this article is 3.11.9 or 3.8.10 (on Win7), PyQt5 version is 5.15.9, and the code has been tested on Windows 7 (6.1), 10 (10.0.19045), and 11 (10.0.22621 and above).
>
> In theory, any Windows Vista and above that can use PyQt5, PyWin32, and ctypes should work.

<p align="center">--- The main content begins ---</p>

## 1. First, create a frameless window

Let's look at the code:

<<< @/public/windows-pyqt5-frameless-window-show-system-buttons/code-1.py{16,17}

This "frameless" approach might differ from what you commonly use. It doesn't modify `windowFlags`. Instead, it removes the standard window frame by handling the `WM_NCCALCSIZE` native event, making the window "frameless" while retaining its original `windowFlags`.

The result is as follows:

![A blank frameless window, no border, no title bar, no shadow](/windows-pyqt5-frameless-window-show-system-buttons/code-1.png)

The difference from a regular `Qt.FramelessWindowHint` is that this window still has a system menu (try pressing `Alt` + `Space`), and it can be maximized and minimized.

## 2. Add window shadows

Again, look at the code:

<<< @/public/windows-pyqt5-frameless-window-show-system-buttons/code-2.py

> [!IMPORTANT]
>
> This code uses a library called [`PyQt5-Frameless-Window`](https://github.com/zhiyiYo/PyQt-Frameless-Window), which encapsulates a cross-platform frameless window. In this article, I only use the C structures, some utility functions, and other bits from the implementation details of this library, not the window part of it.

Let's examine `nativeEvent`. In the `WM_NCCALCSIZE` handling section, I added some calculations (L29~38). These calculations modify the margins of the window's non-client area (NCA), allowing the resizing border to behave identically to the standard window frame's resizing behavior (essentially, the left, bottom, and right borders are handed over to the standard window frame, which provides shadows and the same resizing behavior as a "window with borders").

Now, observant readers might ask:

> Why not adjust the top border margin as well?

Well, indeed, you cannot adjust **all** four borders, otherwise, you'll get strange results. Feel free to try it yourself, haha.

Next is `WM_NCHITTEST`: this compensates for not adjusting the top border — with this, the top border can also be used for resizing.

Now, look at `WM_DPICHANGED` below (the constant I used isn't in `win32con`). This handling is mainly to adapt the `resizeBorderThickness` to the new DPI when the DPI changes, adjusting the window margins to the new size.

Now, look at `updateFrame`. This is important: without this, the window might not become frameless until you manually resize it after it appears. The purpose of this function is to automatically refresh the frame.

Alright, let's see the effect:

![A blank frameless window, with shadow added, resizable on all four sides compared to the previous one](/windows-pyqt5-frameless-window-show-system-buttons/code-2.png)

Now that we have shadows and resizing capabilities, it's time to get back to the main topic:

## 3. Custom title bar + system buttons

As usual, look at the code first:

<<< @/public/windows-pyqt5-frameless-window-show-system-buttons/code-3.py

Now look at the effect:

![A window with a title bar, no icon or title on the title bar, but with system buttons; the content area below is black, and the window border is white](/windows-pyqt5-frameless-window-show-system-buttons/code-3.png)

Let's examine `__init__`. Added `titleBar`, which is the standard title bar from `PyQt5-Frameless-Window`, featuring a window icon, title, and three buttons. In this example, we have system buttons, so we hide the buttons provided by the title bar.

`__init__` also contains a [`DwmDefWindowProc`](https://learn.microsoft.com/windows/win32/api/dwmapi/nf-dwmapi-dwmdefwindowproc) declaration. This is an important Windows API function exported by dwmapi.dll. We declare its parameter and return types here; its purpose will be explained later.

Next is a call to `setStyleSheet` to clear the theme's default background; due to DWM characteristics, system buttons are at the lowest Z-order of window controls (below the background). Therefore, controls or backgrounds can obscure the system buttons.

Then, resizing is done because adding controls can make the window very small (the initial size of `StandardTitleBar`).

In the `updateFrame` method, the call to [`DwmExtendFrameIntoClientArea`](https://learn.microsoft.com/windows/win32/api/dwmapi/nf-dwmapi-dwmextendframeintoclientarea) extends the upper part of the window down by the height of a standard title bar (note: this is not hardcoded to 32px, but obtained from the [`GetSystemMetrics`](https://learn.microsoft.com/windows/win32/api/winuser/nf-winuser-getsystemmetrics) function for the title bar height plus the resizing border thickness). In this extended area, the system provides the system buttons. Therefore, this is the most crucial part.

Next, the code in `resizeEvent` simply adjusts the title bar control to match the window's width.

Then we reach the **most important** part: `nativeEvent`! Here, the [`DwmDefWindowProc`](https://learn.microsoft.com/windows/win32/api/dwmapi/nf-dwmapi-dwmdefwindowproc) function is called. Its purpose is to handle interactions with the system buttons, such as hover (mouse pointer over a button), click, leave, etc. Without this section, the system buttons would be mere decorations, incapable of any action.

Some details need clarification:

1. As you can see, similar to Windows Explorer, the window border becomes white. This issue only occurs on Windows 10; other versions do not exhibit this:
    - When the [`MARGINS`](https://learn.microsoft.com/windows/win32/api/uxtheme/ns-uxtheme-margins) passed to [`DwmExtendFrameIntoClientArea`](https://learn.microsoft.com/windows/win32/api/dwmapi/nf-dwmapi-dwmextendframeintoclientarea) contain positive values, the window border is white.
    - When the [`MARGINS`](https://learn.microsoft.com/windows/win32/api/uxtheme/ns-uxtheme-margins) passed to [`DwmExtendFrameIntoClientArea`](https://learn.microsoft.com/windows/win32/api/dwmapi/nf-dwmapi-dwmextendframeintoclientarea) contain negative values, the window border... doesn't appear at all!
    - When all values in the [`MARGINS`](https://learn.microsoft.com/windows/win32/api/uxtheme/ns-uxtheme-margins) passed to [`DwmExtendFrameIntoClientArea`](https://learn.microsoft.com/windows/win32/api/dwmapi/nf-dwmapi-dwmextendframeintoclientarea) are 0 (the default), the window border is the normal dark gray (may vary with theme mode).

2. When maximized, part of the window's "title bar" area, equal to `resizeBorderThickness`, is pushed off-screen. This is likely to prevent users from resizing the window when maximized, but... this behavior is quite peculiar! Why not simply disable it, rather than moving the resizable area off-screen? However, this is a Microsoft-imposed *rule* we cannot change. To prevent controls on the title bar from not being vertically centered, you can adjust the title bar's height, reposition the window's controls, or adjust the layout's `contentsMargins` (if any).

    > Actually, there is a simpler method. You can check if the window is maximized when handling `WM_NCCALCSIZE` and adjust the top margin (all four margins can be adjusted when maximized without causing strange behavior) by adding `resizeBorderThickness`. This achieves the effect without modifying window properties. Unfortunately, this approach is not friendly to windows with system buttons, as adjusting the top margin when maximized causes the system buttons to stop responding again (whether it's a bug or not is unknown), so other methods must be attempted.

Through the above content, you now have a window containing system buttons. These buttons automatically switch their styles according to the theme settings. Go ahead and use it!

## Notes

1. The system button window implemented via this method is not perfect because it does not support opening the [system menu](https://learn.microsoft.com/windows/win32/menurc/about-menus#the-window-menu) by clicking the window icon or right-clicking the title bar. I have implemented a version that includes the system menu [here](https://gist.github.com/xiaoshu312/291999ae2c726b966ca2d2bc4b9a810d), but it still has some issues. Feel free to take a look if interested!

2. Regarding the maximization issue, Chromium has a good solution, but I haven't investigated it yet.

    > [!TIP]
    >
    > Did you know? On Windows 11, launching Chromium with the `--enable-features=Windows11MicaTitlebar` parameter starts Chromium with system buttons!
    >
    > [![Microsoft Edge with system buttons](/windows-pyqt5-frameless-window-show-system-buttons/microsoft-edge-mica-windows-11-hero.webp)](https://pureinfotech.com/microsoft-edge-mica-material-windows-11/)
    >
    > Note: The Microsoft Edge in the image is also based on the Chromium kernel. (I probably didn't need to mention that)

## References

1. [Custom Window Frame Using DWM - Microsoft Learn](https://learn.microsoft.com/windows/win32/dwm/customframe)
2. [c++ - Why is my DwmExtendFrameIntoClientArea()'d window not drawing the DWM borders? - Stack Overflow](https://stackoverflow.com/questions/41106347/why-is-my-dwmextendframeintoclientaread-window-not-drawing-the-dwm-borders)
3. [zhiyiYo/PyQt-Frameless-Window: A cross-platform frameless window based on PyQt/PySide, support Win32, Linux and macOS.](https://github.com/zhiyiYo/PyQt-Frameless-Window)