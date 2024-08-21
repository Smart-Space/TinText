# TinML转译HTML

新版TinML增加了实用性作为标准特性之一，需要具备实用功能，转译HTML就是其中之一。

下方是一段TinML：

```
<title>一级标题|
<title>二级标题|2
<title>三级标题|3
<title>四级标题|4
<title>五级标题|5
<title>六级标题|6

<p>

<p>/*-_普通文本;
|直接使用<p>来表示，
|-comment

|结尾会自带换行。|
```

经过转译后，形成下方HTML：

```html
      <h1>一级标题</h1>
      <h2>二级标题</h2>
      <h3>三级标题</h3>
      <h4>四级标题</h4>
      <h5>五级标题</h5>
      <h6>六级标题</h6>
      <p><br></p>
      <p>
        <s>
          <u><i>
              <b>普通文本</b>
            </i></u>
        </s>直接使用<p>来表示，结尾会自带换行。
      </p>
```

TinML转译HTML原理简述见[python.tkinter设计标记语言(转译2-html)_tkinter html-CSDN博客](https://blog.csdn.net/tinga_kilin/article/details/140995975)。

**注意，TinML并没有规定如何转译为HTML**。转译为HTML是标准TinML实现中的必需功能，该模块是TinText实现中的转译HTML功能部件。
