"""
/lib/gui/utils.py
TinText界面功能中的杂项功能
"""

def bind(name,seq,func):
    """
    绑定事件
    """
    return name.bind(seq,func)