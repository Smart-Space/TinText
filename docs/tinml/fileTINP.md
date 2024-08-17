# TINP文件

## 简述

TINP文件为TinML的加密文件。

## 后缀名

`*.tinp`

## 编码

UTF-8

---

## 描述

TINP文件本质上是一种加密后的文本文件，是对TinML源码进行加密处理的结果文件。

### 开头约定

标记文本部分，和[TIN文件](fileTIN)一样。

另外，执行下方**加密方法**的开头约定。

### 文本内容

TinML源码加密后的结果。

### 写入

按UTF-8，保留编码写入。

### 读取

按UTF-8，保留编码读取。

---

## 加密方法

本条目规定TINP生成方法，读取与解算方法由各个实现平台决定。

### XOR加密

基于XOR的简单加密方法。

根据现有TinML文本，直接获取`TinML text`。

随机计算出一串文本加一个换行符，得到`head`，添加在`TinML text`前，得到`code text`。

获取密码`key`，长度不得大于`code text`。

> 注意，TINP未对`key`作任何要求，只要Unicode存在对应的字符即可。数字、符号、各种语言的文字、表情均可。

如果`key`长度小于`code text`，循环填充`key`得到`code key`，比如`key->keykeykeyk...`，使其长度与`code text`相当。

如果`key`长度等于`code text`，直接获得`code key`

获取`code text/key`的Unicode代码点`u text/key`。

两者从头到尾逐个对应，进行XOR运算，将结果返回为Unicode字符`result`。

将`result`以utf-8编码，保留空白字符编码的方式写入TINP文件。
