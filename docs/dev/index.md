# TinText Development

首先说明，想靠简单的几个文件是无法解释清楚TinText项目的全部的，作为练习项目，TinText不会提供完整的开发文档，具体内容看看简单的源码便可知。

TinText的整体结构分为两部分，GUI部分和非GUI文件处理部分。

---

## 界面

由`gui.py`总管理，下属`lib.gui`和`lib.TinEngine`两部分。

### gui

负责部分如下：

- `utils` - TinText GUI 实用工具

- `reader` - 主界面 阅读器

- `writer` - 编辑器

- `maker` - TIN文件加密与集成应用

- `writertools` - TinWriter工具部件

### TinEngine

负责部分如下：

- `TinEngineCore` - [TinEngine核心TinText控件](tinengine)

- `tin2html` - [TinML与转译html支持](tinengine/tin2html)

- `controls` - TinEngine使用的内部控件

- `error` - TinEngine定义的错误

- `structure` - TinEngine的特殊数据类型

---

## 非界面

由`process.py`总管理，下属`lib.process`

### process

负责部分如下：

- `multi` - [子进程通信](process)

- `configfile` - 配置文件

- `version` - 版本操作
