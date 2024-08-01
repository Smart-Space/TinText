"""
TinEngine异常类
"""

class TagNoMatch(Exception):
    #TinParser无法匹配的tin标记
    def __init__(self, msg):
        super().__init__(msg)
        self.msg=msg
    def __str__(self) -> str:
        return self.msg


class NoLinesMode(Exception):
    #没有在多行模式下，但是出现了多行参数表达
    def __init__(self, msg):
        super().__init__(msg)
        self.msg=msg
    def __str__(self) -> str:
        return self.msg

class NoLinesMark(Exception):
    #标签的多行模式时没有多行参数
    def __init__(self, msg):
        super().__init__(msg)
        self.msg=msg
    def __str__(self) -> str:
        return self.msg

class AlreadyStartLine(Exception):
    #已经开启了多行表达
    def __init__(self,msg):
        super().__init__(msg)
        self.msg=msg
    def __str__(self) -> str:
        return self.msg
