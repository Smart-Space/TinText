# TinText

新版TinML的首次实现。

根据新版TinML标准，TinText不仅实现了对Tin标记文本的阅读、编辑，还增加了对TIN文件相关实用功能的支持。

## TinReader

[TinReader](reader)是TinText的阅读器，同时也是主窗口，指向TinText应用组的所有功能入口。

## TinWriter

[TinWriter](writer)是TinText的编辑器。

## TinMaker

[TinMaker](maker)是TinText的TIN文件加密与集成应用。

---

## 后台操作

为了不影响TinText应用组正常使用，同时自动完成后台文件与配置等的管理作业，TinText会自动执行一些后台操作。

### 图片清理

`./data/imgs/*`下的文件保存期限为60天，超过60天的，当TinText开启时自动在后台进行清理。如果想要保留图片文件，请通过TinML源码找到图片名称，从图片目录中获取图片文件。

### tinfile文件清理

`./data/tinfile/user/*`下的文件保存期限为60天，超过0天的，当TinText开启时自动在后台进行清理。

这个文件夹主要是`TinText`获取在线tinfile存放的文件目录，也是`<tinfile>`标签查询插入文件的起始目录。

### 版本信息获取

该操作涉及微量网络流量使用，当用户点击“获取最新版本信息”时，TinText会在后台连接官网，获取最新版本号。
