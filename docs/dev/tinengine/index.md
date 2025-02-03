# TinEngineCore

TinEngine是TinText（应用组）实现TinML渲染和转译的核心部件，TinEngineCore则是实现TinEngine的直接接口，内含`TinParser`（解析类）和`TinText`（控件）。

其中，`TinText`使用的[子线程退出机制](thread_out)有专门的篇幅介绍。

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

### parse(tin:str)

此方法用于将TinML标记文本转为`TinText`能够解析的结构。

> `TinText`本身的渲染方法直接调用了`TinParser.parse`。

每一个标签块通过`yield`输出，例如：

```tinml
<title>标题|2
```

输出：

```python
(1, '<title>', ('标题','2'))
```

- 第一个参数为标签块所处的行数，如果是多行标签，则为起始标签所在的行数
- 第二个参数为标签名称
- 第三个参数为标签标记内容

但是，如果标记块不符合TinML规范，则会**输出**错误（不是抛出）：

- `NoLinesMode`标记未使用多行表达，但是出现了多行表达的开头标记`|`
- `NoLinesMark`开启了多行表达，但是接下来没有使用多行表达开头标记
- `TagNoMatch`正则匹配无法匹配到标签名称
- `AlreadyStartLine`重复开启多行表达

---

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

### render(tintext:str, new=True)

此方法用于将TinML标记文本进行渲染呈现。

当`new = True`时，则会清除已有内容和上下文标记，重新开始渲染任务。

### thread_render(tintext:str, wait=False, new=True, in_queue=False)

此方法用于将TinML标记文本在子线程中进行渲染呈现。

当`wait = True`时，渲染线程将阻塞主线程。如果是一般渲染，建议将此值设`False`，而不是直接使用`render`方法。

当`new = True`时，则会清除已有内容和上下文标记，重新开始渲染任务。

当`in_queue = True`时，则会在正在渲染时将标记文本添加到待渲染队列中，但此时`wait`和`new`参数都不会起作用。

如果当前没有渲染线程，或者当前正在渲染，而指定将标记文本添加到待渲染队列，该方法均会返回`True`，代表渲染申请得到处理。否则返回`False`，代表不会渲染。
