# [Windows] 在 PyQt5 的无边框窗口中显示系统按钮

## 引子

在使用 Windows 上的很多软件的时候，我们会发现有些软件的窗口比较奇怪，就像这些：

![Microsoft Word 2007 中的自定义框架](/windows-pyqt5-frameless-window-show-system-buttons/word2007-customframe.png)

![Windows 10 的 Explorer 中的自定义框架](/windows-pyqt5-frameless-window-show-system-buttons/explorer10-customframe.png)

我们都知道，（正常情况下）窗口边框上的内容由操作系统进行管理，应用程序是无法触及的，但是这些窗口却可以在标题栏上放置自己的控件，同时保留系统自带的（原生）标题栏按钮，这是怎么做到的呢？

> [!TIP]
>
> 本文中使用的 Python 版本为 3.11.9 ， PyQt5 版本为 5.15.9 ，并在 Windows 7 (6.1), 10 (10.0.19045), 11 (10.0.22621 以上) 对代码进行了测试
>
> 理论上任何能使用 PyQt5、PyWin32、ctypes 的 Windows Vista 及以上的 Windows 都可以使用

<p align="center">--- 正片开始 ---</p>

## 1. 先得有个无边框窗口

先看代码：

<<< @/public/windows-pyqt5-frameless-window-show-system-buttons/code-1.py{16,17}

这个“无边框”可能与你们经常使用的代码有些不同。它没有修改 `windowFlags` ，而是通过处理 `nativeEvent` 的 `WM_NCCALCSIZE` 删除了窗口的标准窗口框架，使这个窗口在成为了“无边框窗口”的同时保留窗口原有的 `windowFlags` 。

效果如下：

![一个空白的无边框窗口，没有边框，没有标题栏，没有阴影](/windows-pyqt5-frameless-window-show-system-buttons/code-1.png)

与普通的 `Qt.FramelessWindowHint` 不同的点在于，它有系统菜单（不信你按下 `Alt` + `Space` 试试），能最大化、最小化。

## 2. 加上窗口阴影

还是先看代码：

<<< @/public/windows-pyqt5-frameless-window-show-system-buttons/code-2.py

> [!IMPORTANT]
>
> 这段代码使用了一个名为 [`PyQt5-Frameless-Window`](https://github.com/zhiyiYo/PyQt-Frameless-Window) 的窗口库，这个库封装了一个跨平台的无边框窗口，在本文中我只使用了此窗口库实现细节中的 C 结构体、一些实用的函数和一些其他的东西，并没有用到这个库的窗口部分。

先来看看 `nativeEvent` 。我在处理 `WM_NCCALCSIZE` 的部分添加了一些运算（L29~38），这些运算可以改变窗口的非客户区（Non-Client Area, NCA）的边距，使它能够调整大小的边框与标准的窗口框架的边框行为一致（实际上就是把左、下、右的边框部分让给了标准窗口框架，这样才会有阴影和与“有边框窗口”相同的调整大小的行为。）

那这个时候，仔细观察的小伙伴可能就有疑问了：

> 那为什么不调整上边框的边距呢？

嗯，确实不能四个边框**全**都调整，不然就会有奇怪的结果，你可以自己去试试，哈哈。

接下来是 `WM_NCHITTEST` ：这里弥补了不调整上边框的结果——加上这个，上边框也能调整大小了。

好了，我们再来看看下面的 `WM_DPICHANGED` （我使用的 `win32con` 里没有这个常量）。这个处理主要是为了在 DPI 改变时能匹配新 DPI 的 `resizeBorderThickness` ，调整窗口边距为新的大小。

现在来看 `updateFrame` 。这里很重要：如果不加上这个，很可能窗口出现之后需要手动调整大小才能让你的窗口变成无边框窗口。这个函数的作用就在于自动刷新框架。

好了，来看效果：

![空白的无边框窗口，比刚才那个多了阴影，四边都能调整大小](/windows-pyqt5-frameless-window-show-system-buttons/code-2.png)

现在有了阴影，能调大小，就该回归正题了：

## 3. 自定义标题栏 + 系统按钮

老规矩，先看代码：

<<< @/public/windows-pyqt5-frameless-window-show-system-buttons/code-3.py

再看效果：

![一个有标题栏的窗口，标题栏上没有图标和标题，但是有系统按钮，下面的内容区域是一片黑色，窗口边框是白色的](/windows-pyqt5-frameless-window-show-system-buttons/code-3.png)

这里有一些细节需要说明：
