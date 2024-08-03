"""
/lib/gui/utils.py
TinText界面功能中的杂项功能
"""
from tkinter import CallWrapper


#_register, bind重写，用于通过tcl命令创建的控件的事件绑定
def _register(func, subst=None, widget=None, needcleanup=1):
    """
    返回tcl注册函数
    """
    f=CallWrapper(func,subst,widget).__call__
    name=repr(id(f))
    try:
        func = func.__func__
    except AttributeError:
        pass
    try:
        name = name + func.__name__
    except AttributeError:
        pass
    widget.tk.createcommand(name,f)
    if needcleanup:
        if widget._tclCommands is None:
            widget._tclCommands = []
        widget._tclCommands.append((name, f))
    return name
def bind(widget,name,seq=None,func=None,add=None):
    """
    绑定事件，主要供peer产生的文本框使用
    widget作为tcl解释器来源，需要给出，
    且最好是源头文本框，否则可能无法绑定
    目前，func没有event参数
    """
    if isinstance(func, str):
        widget.tk.call('bind',name,seq,func)
    elif func:
        funcid=_register(func,widget._substitute,widget)
        cmd = ('%sif {"[%s %s]" == "break"} break\n'
                %
                (add and '+' or '',
                funcid, widget._subst_format_str))
        widget.tk.call('bind',name,seq,cmd)
        return funcid
    elif seq:
        return widget.tk.call('bind',name,seq)
    else:
        return widget.tk.splitlist(widget.tk.call('bind',name))