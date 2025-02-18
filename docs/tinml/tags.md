# TinML标签

以下根据标准标签名字母顺序排列。

`[arg]`为可选参数

> 本页面只给出标签名与位置参数、标记的标准规定，此外不作额外说明。具体用法请查看具体TinML实现平台的说明。

---

## \<ac\>(#)name

**锚点**

- 锚点名称。在当前位置添加锚点标记。如果名称前含`#`，则在当前位置插入锚点文本`🔗`，点击前往对应的锚点

*另外支持：\<anchor\>*

---

## \<code\>type;

## |code1

## |code2

## |code3...|

**高亮代码**

- 代码类型。应为小写全称

- 代码片段

---

## \<fl\>

**跟随显示**

每次使用切换跟随显示的状态，默认关闭

*另外支持：\<follow\>*

---

## \<html\>html1|html2|...|

**超文本渲染块**

- html文本。HTML文本完全可以写在一个内容参数里。**虽然TinML标准支持HTML，但是<u>不建议</u>使用`<html>`**

---

## \<img\>name|[url]|[size]

**图片**

- 图片文件名

- 图片地址

- 图片尺寸。支持`数字x数字`，`百分比x百分比`（以当前渲染窗口尺寸为100%），`百分比x数字`（可调换），第一个数字是宽度，第二个数字是高度。百分比需要使用百分号`%`

如果`name`存在，并且本地`./data/imgs/`下存在相对目录、名称一致的图片，则有限使用本地图片

*另外支持：\<image\>*

---

## \<lnk\>text|url|[description]

**超链接**

- 文本

- 链接地址

- 描述。若为空，则使用链接地址

*另外支持：\<link\> \<a\>*

---

## \<ls\>list1;

## |list2

## |list3...|

**无序列表**

- 列表内容

一块列表内容使用一个列表标签元素，每个参数代表一行标签内容。

每级内容使用开头标记“I”确定，最多支持四级内容，即三个“I”。

*另外支持：\<list\>*

---

## \<n\>note1|[note2]|...

**引用说明文本**

- 文本

*另外支持：\<note\>*

---

## \<nl\>list1;

## |list2

## |list3...|

**有序列表**

- 列表内容

一块列表内容使用一个列表标签元素，每个参数代表一行标签内容。

每级内容使用开头标记“I”确定，最多支持四级内容，即三个“I”。

*另外支持：\<numlist\>*

---

## \<p\>text1|[text2]|...

**文本块**

- 文本。文本开头标记可以混合使用，但必须连续

如果文本开头为空格，则忽略第一个空格，从第二个字开始记作该文本的呈现内容。如` *text`，则呈现`*text`；如`  text`，则呈现` text`。

同理，如果标识符后跟空格，则标识符识别到此位置停止，忽略这个空格，从下一个字开始记作该文本的呈现内容。如`* -text`，则呈现`-text`；如`*  -text`，则呈现` -text`。

超链接必须使用`![...](...)`格式，标记符号需要连起来。

| 文本开头标记   | 含义              |
| -------- | --------------- |
| \*       | **粗体**          |
| /        | *斜体*            |
| -        | ~~删除线~~         |
| __       | <u>下划线</u>      |
| ^        | <sup>上标</sup>   |
| &（与^不共存） | <sub>下标</sub>   |
| =        | <mark>高亮</mark> |
| #（与=不共存） | `代码`            |
| \!\[\]() | [超链接]()         |

*另外支持：无标签文本段*

---

## \<pages>name1|name2|[name3]...

## ...

## \</page\>

## ...

## \</page\>

## ...

## \</pages>

**标签页**

- 标签页标题。至少两个

`<pages>`注明标签页名称、数量、顺序，下方内容块数量和顺序与之对应

不同标签页内容之间使用`</page>`分割。最后一块内容不需要分割标签与其它内容块做区分，直接使用结束标签`</pages>`

---

## \<part\>name

## ...

## \</part\>name

**可选择是否阅读的文本片段**

- 片段名称

使用时需注意包含关系，如果在`<part>part1`开始后，`</part>part1`在`<part>part2`与`</part>part2`之间，而`part2`未被展开阅读，则`part1`的作用域会一致持续。为了避免这一逻辑错误，实现平台可以直接阻止这一种写法。

*另外支持：\<pt\> \</pt\>*

---

## \<sp\>[color]

**分割线**

- 颜色

*另外支持：\<separate\>*

---

## \<stop\>time

**渲染暂停**

- 暂停时间

---

## \<tb\>head1|head2|[head3]|...

## \<tb\>data1|data2|[data3]|...

## ...

## \</tb\>

**表格**

- 表头，至少两个

- 多行表格内容（至少一行），数量与表头一致

渲染位置由结束标签决定

*另外支持：\<table\> \</table\>*

---

## \<tin\>...

**TinML标记**

- 任意文本

---

## \<tinfile>name|[mode]

**嵌入tinml文件**

- tinml文件名称。包括后缀名
- 模式。默认`append`，在现有内容后面追加指定TinML文件文本段；`inner`，以内嵌`TinText`的方式，将指定TinML文件在全新、完整`TinEngine`环境中解释渲染

在`./data/tinfile/user/`目录下寻找`name`指定的TinML文件并嵌入到当前解释渲染结果界面。

当前支持格式：`*.tin`

---

## \<title\>title|[level]

**标题**

- 标题文本

- 标题层级。1~6

*另外支持：\<t\>*

---

## \<wait\>content

**暂停渲染并等待阅读**

- 提示阅读内容。暂停渲染，由读者确定何时开始显示接下来的内容

*另外支持：\<w\>*

---

TinML只给出Tin标记文本标准。

解释、渲染、转译等具体操作由各个实现平台决定。

---

## 优先级

控制标签>元素标签
