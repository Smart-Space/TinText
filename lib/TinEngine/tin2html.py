"""
tin->html工具类
"""
from html.parser import HTMLParser

class TinML(list):
    """
    tin->html的中间工具
    本质上是一个大型列表，可嵌套
    addtin(tag, **kw) - 加载tin解析内容
    clear() - 清空
    """

    def __init__(self):
        super().__init__()

    def addtin(self,tag,**kw):
        super().append((tag,kw))

    def clear(self):
        super().clear()


class TinTranslator():
    """
    tin->html的转译工具类
    *后续可能支持tin->markdown
    """

    def __init__(self):
        pass

    def tohtml(self,tinml:TinML):
        #tin->html
        ...
