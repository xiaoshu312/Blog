# [Windows] Display System Buttons in a PyQt5 Frameless Window

## Introduction {#Introduction}

When using many software applications on Windows, we sometimes notice that some windows look a bit unusual, like these:

![Custom Frame in Microsoft Word 2007](/windows-pyqt5-frameless-window-show-system-buttons/word2007-customframe.png)

![Custom Frame in Windows 10 Explorer](/windows-pyqt5-frameless-window-show-system-buttons/explorer10-customframe.png)

As we know, (normally) the content on the window border is managed by the operating system, and applications cannot interfere. However, these windows can place their own controls on the title bar while retaining the system's native title bar buttons. How is this achieved?

> [!TIP]
>
> The Python version used in this article is 3.11.9 or 3.8.10 (on Win7), PyQt5 version is 5.15.9. The code has been tested on Windows 7 (6.1), 10 (10.0.19045), and 11 (10.0.22621 and above).
>
> In theory, this should work on any Windows Vista and above system that can use PyQt5, PyWin32, and ctypes.

<p align="center">--- Let's Begin ---</p>

## 1. First, Get a Frameless Window {#First}

Let's look at the code:

<<< @/public/windows-pyqt5-frameless-window-show-system-buttons/code-1.py{16,17}

This "frameless" approach might differ from the code you usually use. It doesn't modify `windowFlags`. Instead, it removes the standard window frame by handling the `WM_NCCALCSIZE` event in `nativeEvent`, making the window "frameless" while retaining its original `windowFlags`.

The result looks like this:

![A blank frameless window, no border, no title bar, no shadow](/windows-pyqt5-frameless-window-show-system-buttons/code-1.png)

The difference from the ordinary `Qt.FramelessWindowHint` is that it has a system menu (try pressing `Alt` + `Space`), and it can be maximized and minimized.

## 2. Add Window Shadows {#Second}

Let's look at the code again:

<<< @/public/windows-pyqt5-frameless-window-show-system-buttons/code-2.py

> [!IMPORTANT]
>
> This code uses a window library called [`PyQt5-Frameless-Window`](https://github.com/zhiyiYo/PyQt-Frameless-Window), which encapsulates a cross-platform frameless window. In this article, I only use the C structures, some utility functions, and other elements from the implementation details of this library, not the library's window part itself.

First, let's look at `nativeEvent`. In the part handling `WM_NCCALCSIZE` (L29~38), I've added some calculations. These calculations can change the margins of the window's Non-Client Area (NCA), making the resizable border behave identically to the standard window frame's border (essentially, it delegates the left, bottom, and right border areas to the standard window frame, so it will have shadows and the same resizing behavior as a "window with a frame").

At this point, observant readers might have a question:

> Why not adjust the top border margin as well?

Well, you really can't adjust **all** four borders; otherwise, you'll get strange results. Feel free to try it yourself, haha.

Next up is `WM_NCHITTEST`: This compensates for not adjusting the top border — with this, the top border can also be used for resizing.

Alright, let's look at `WM_DPICHANGED` below (the constant I used from `win32con` doesn't have this one). This handling is mainly to match the `resizeBorderThickness` to the new DPI when the DPI changes, adjusting the window margins to the new size.

Now let's look at `updateFrame`. This is important: Without this, it's likely that after the window appears, you'd need to manually resize it for it to become a frameless window. The purpose of this function is to automatically refresh the frame.

Okay, let's see the effect:

![A blank frameless window, with shadows added compared to the previous one, and resizable on all four sides](/windows-pyqt5-frameless-window-show-system-buttons/code-2.png)

Now that we have shadows and can resize, it's time to get back to the main topic:

## 3. Custom Title Bar + System Buttons {#Third}

As usual, let's look at the code first:

<<< @/public/windows-pyqt5-frameless-window-show-system-buttons/code-3.py

Now let's see the effect:

![A window with a title bar, no icon or title on the title bar, but with system buttons, the content area below is black, and the window border is white](/windows-pyqt5-frameless-window-show-system-buttons/code-3.png)

Look at `__init__`. A `titleBar` has been added. This is the standard title bar from `PyQt5-Frameless-Window`, which includes a window icon, title, and three buttons. In this example, we have system buttons, so we don't need the buttons provided by the title bar and hide them.

There's also [`DwmDefWindowProc`](https://learn.microsoft.com/windows/win32/api/dwmapi/nf-dwmapi-dwmdefwindowproc) in `__init__`. This is a very important Windows API function, exported by dwmapi.dll. We declare its parameter and return types here; we'll discuss its purpose later.

Next is a call to `setStyleSheet` to clear the theme's default background. Due to DWM's characteristics, system buttons are at the bottom of the window control Z-order (below the background). Therefore, controls or the background can obscure the system buttons.

Then, we resize the window because adding controls would otherwise make the window very small (the initial size of `StandardTitleBar`).

In the `updateFrame` method, the call to [`DwmExtendFrameIntoClientArea`](https://learn.microsoft.com/windows/win32/api/dwmapi/nf-dwmapi-dwmextendframeintoclientarea) extends the top part of the window frame down into the client area by the height of a standard title bar (note, this isn't hardcoded to 32px, but obtained from the [`GetSystemMetrics`](https://learn.microsoft.com/windows/win32/api/winuser/nf-winuser-getsystemmetrics) function: the title bar height plus the resizing border thickness). Within this extended area, the system provides the system buttons. Therefore, this is the most crucial part.

Next, the code in the `resizeEvent` handler simply adjusts the title bar control to match the window's width.

Then we enter the **most important** `nativeEvent`! Here, the [`DwmDefWindowProc`](https://learn.microsoft.com/windows/win32/api/dwmapi/nf-dwmapi-dwmdefwindowproc) function is called. Its role is to handle interactions with the system buttons, such as hover, click, leave, etc. Without this part, the system buttons would be just decorative and non-functional.

Some details need clarification here:

1.  As you might have noticed, similar to Windows Explorer, the window border becomes white. This issue only occurs on Windows 10; other versions don't exhibit it:
    - When the values in the [`MARGINS`](https://learn.microsoft.com/windows/win32/api/uxtheme/ns-uxtheme-margins) structure passed to [`DwmExtendFrameIntoClientArea`](https://learn.microsoft.com/windows/win32/api/dwmapi/nf-dwmapi-dwmextendframeintoclientarea) are all non-negative, the window border is white.
    - When the [`MARGINS`](https://learn.microsoft.com/windows/win32/api/uxtheme/ns-uxtheme-margins) structure contains negative values, the window border... doesn't show up at all!
    - When all values in the [`MARGINS`](https://learn.microsoft.com/windows/win32/api/uxtheme/ns-uxtheme-margins) are 0 (the default case), the window border is the normal dark gray (which may vary with the theme mode).

2.  When maximized, the part of the window "title bar" with the height of `resizeBorderThickness` gets pushed off-screen. This is probably to prevent users from resizing the window when maximized, but... this operation is quite peculiar! Why not just disable it, and instead move the resizable area off-screen? But this is a *rule* set by Microsoft, and we can't change it. To prevent controls on the title bar from not centering vertically, you can adjust the title bar's height, reposition the window's controls, or adjust the layout's `contentsMargins` (if any).

    > Actually, there is a simpler method. You can check if the window is maximized while handling `WM_NCCALCSIZE` and adjust the top margin accordingly (adjusting all four borders when maximized doesn't cause strange behavior), adding the `resizeBorderThickness` to the top. This achieves the effect without modifying window properties. Unfortunately, this method is not friendly to windows containing system buttons, because adjusting the top margin when maximized causes the system buttons to stop responding again (not sure if it's a bug). So, other methods must be tried.

Through the content above, you now have a window containing system buttons. The buttons on this window can automatically switch according to the theme's button styles. Go ahead and use it!

## Remarks {#Remarks}

1.  The system button window implemented through the above method is not perfect because it does not support opening the [system menu](https://learn.microsoft.com/windows/win32/menurc/about-menus#the-window-menu) by clicking the window icon or right-clicking the title bar. I have implemented a version [here](https://gist.github.com/xiaoshu312/291999ae2c726b966ca2d2bc4b9a810d) that includes a system menu, but it still has some issues. Feel free to check it out if you're interested!

2.  Regarding the maximization issue, Chromium seems to have a good solution, but I haven't looked into it yet.

    > [!TIP]
    >
    > Did you know? On Windows 11, starting Chromium with the `--enable-features=Windows11MicaTitlebar` parameter launches Chromium with system buttons!
    >
    > [![Microsoft Edge with system buttons](/windows-pyqt5-frameless-window-show-system-buttons/microsoft-edge-mica-windows-11-hero.webp)](https://pureinfotech.com/microsoft-edge-mica-material-windows-11/)
    >
    > Note: Microsoft Edge in the picture is also based on the Chromium engine. (I probably don't need to mention this)

3.  On Windows 11, the window above might not have the Mica effect. To enable it, simply add the following before the `updateFrame` call in `__init__`:

    ```python
        if win32_utils.isGreaterEqualWin11():
            self.windowEffect.setMicaEffect(self.winId())
            # or use self.windowEffect.setMicaEffect(self.winId(), False, True) to enable MicaAlt effect
    ```

    You will then see the Mica effect on the title bar. For more information about `WindowEffect`, see [window_effect.py](https://github.com/zhiyiYo/PyQt-Frameless-Window/blob/master/qframelesswindow/windows/window_effect.py).

    ::: details Mica (Alt) Effect

    ![Window with Mica effect enabled](/windows-pyqt5-frameless-window-show-system-buttons/win11-mica-window.png)

    ![Window with Mica Alt effect enabled](/windows-pyqt5-frameless-window-show-system-buttons/win11-mica-alt-window.png)

    ![Window with Mica effect enabled, with a custom button on the title bar](/windows-pyqt5-frameless-window-show-system-buttons/win11-custom-button.png)

    :::

## References {#References}

1.  [Custom Window Frame Using DWM - Microsoft Learn](https://learn.microsoft.com/windows/win32/dwm/customframe)
2.  [c++ - Why is my DwmExtendFrameIntoClientArea()'d window not drawing the DWM borders? - Stack Overflow](https://stackoverflow.com/questions/41106347/why-is-my-dwmextendframeintoclientaread-window-not-drawing-the-dwm-borders)
3.  [zhiyiYo/PyQt-Frameless-Window: A cross-platform frameless window based on PyQt/PySide, support Win32, Linux and macOS.](https://github.com/zhiyiYo/PyQt-Frameless-Window)