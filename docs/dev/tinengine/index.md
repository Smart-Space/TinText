# TinEngineCore

TinEngine是TinText（应用组）实现TinML渲染和转译的核心部件，TinEngineCore则是实现TinEngine的直接接口，内含`TinParser`（解析类）和`TinText`（控件）。

## TinParser 解析类

`TinParser`的主要作用就是将一串TinML文本转为可被进一步解释、渲染的内容参数。

比如以下文本：

```
<title>标题

|-注释（下方<p>在实际写作中不建议多行写法）
<p>这是;
|*文本
|。|
```

这全部是文字，但是需要通过解析形成类似下方的数据：

```python
(
    ('<title>','标题'),
    ('<p>','这是','*文本','。')
)
```

`TinParser`的实现原理简述见[python.tkinter设计标记语言(语法2-语法解析器)](https://blog.csdn.net/tinga_kilin/article/details/140981379)。

## TinText 控件类

`TinText`由两部分功能组成，解释、渲染。这两个功能在同一个模块（`render function`）里，但是有先后之分。

解释，就是将标签参数解释成有意义的内容。还是拿上方生成的数据为例，最终需要转变为如下内容：

```python
(
    ('<title>', {'title':'标题','level':'1'}),
    ('<p>',{'texts':('这是','*文本','。')})
)
```

这部分的简述见[python.tkinter设计标记语言(渲染1-解释器)](https://blog.csdn.net/tinga_kilin/article/details/140985660)。

渲染，就是将这些已经有了具体文本意义和样式意义的内容呈现出来，简述见[python.tkinter设计标记语言(渲染2-渲染器)](https://blog.csdn.net/tinga_kilin/article/details/140985724)。当然，最直观的还是查看`TinEngineCore.py`源代码。
