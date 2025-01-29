# TinText

Tin标记语言渲染的python.tkinter实现。

[TinText网站](https://tintext.smart-space.com.cn/)

## Tin标记语言

一个能够实时呈现渲染的流式标记语言，让读者跟着作者的思维阅读。

---

## 依赖

tinui - 作者本人开源 tkinter UI 库

requests - 网络请求

PIL(pillow) - 图片处理

dominate - html编辑库

html2text - markdown转译技术支持库（不作为TinText主要/必需功能）

Pygments - 代码片段高亮支持

tkinterweb - 简易超文本支持

---

TODO LIST：

- 或许导出html的css支持（单独窗口，所有导出都在TinTranslator）
- 查找的高亮颜色置前
- 持续增加标签支持与html转译支持
- gif专门支持显示
- 支持<tinfile>（<tinf>），导入data/tinfile下的TIN格式文件，可选择直接导入，或者导入在子TinText中
- 本地支持从源文件所在目录找寻图片、tin、tinp文件
- <n>使用内置TinText

……
