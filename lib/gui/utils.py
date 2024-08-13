"""
/lib/gui/utils.py
TinText界面功能中的杂项功能
"""
from tkinter import CallWrapper, Text, Toplevel
import tkinter as tk
from tkinter import ttk

from TinUI import BasicTinUI, TinUIXml


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


class ScrolledText(tk.Text):
    """
    使用ttk重写支持滚动条的文本框
    """
    def __init__(self, master=None, **kw):
        self.frame=tk.Frame(master)

        self.vbar=ttk.Scrollbar(self.frame)
        self.vbar.pack(side='right',fill='y')

        kw.update({'yscrollcommand':self.vbar.set})
        tk.Text.__init__(self,self.frame,**kw)
        self.pack(side='left',fill='both',expand=True)
        self.vbar['command']=self.yview

        text_meths=vars(tk.Text).keys()
        methods=vars(tk.Pack).keys() | vars(tk.Grid).keys() | vars(tk.Place).keys()
        methods=methods.difference(text_meths)

        for m in methods:
            if m[0]!='_' and m!='config' and m!='configure':
                setattr(self,m,getattr(self.frame,m))
    
    def __str__(self):
        return str(self.frame)


#TinWriter的行数显示
class LineViewer(BasicTinUI):
    index=None

    def __init__(self,master,text:Text,*args,**kw):
        """
        初始化，创建行数显示控件
        """
        super().__init__(master,*args,**kw)
        self.text=text
        self.text.bind('<KeyRelease>',self.load_line)
        self.text.bind('<ButtonRelease-1>',self.load_line)
        self.line=self.add_paragraph((1,10),text='Ln: 1\tCol: 1',font='Consolas 10',anchor='w')
        # self.entry=self.add_entry((60,10),width=200,font='Consolas 10',anchor='w')[0]
        # self.add_button2((260,10),text='跳转行号',command=self.jump_line,anchor='w')
    
    def load_line(self,e):
        #显示行号
        index=self.text.index('insert').split('.')
        if index==self.index:
            return
        line=int(index[0])
        column=int(index[1])+1
        self.itemconfig(self.line,text=f'Ln: {line}\tCol: {column}')
        self.index=index
    

class TextFinder(Toplevel):

    index='1.0'#当前搜索位置

    def __init__(self,title='search',text=None,*args,**kw):
        """
        初始化，创建文本查找控件
        """
        super().__init__(*args,**kw)
        self.title(title)
        self.geometry("375x80")
        self.withdraw()
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.close)

        self.text=text
        self.text.tag_config("found", background="yellow")

        self.tinui=BasicTinUI(self)
        self.tinui.pack(expand=True,fill='both')

        with open('./pages/_finder.xml','r',encoding='utf-8') as f:
            xml=f.read()
        self.tinuixml=TinUIXml(self.tinui)
        self.tinuixml.funcs['go_to_search']=self.go_to_search
        self.tinuixml.loadxml(xml)
        self.entry_search=self.tinuixml.tags['entry_search'][0]

    def go_to_search(self,e):
        """
        跳转到查找文本
        """
        self.text.tag_remove('found','1.0','end')
        text=self.entry_search.get()
        if text=='':
            return
        index=self.text.search(text,self.index,stopindex='end')
        if index:
            self.index=index+f'+{len(text)}c'
            self.text.tag_add('found',index,f'{index}+{len(text)}c')
            self.text.mark_set('insert',index)
            self.text.see(index)
        else:
            if self.index=='1.0':
                #无匹配，退出搜索
                self.text.tag_remove('found','1.0','end')
                return
            self.index='1.0'
            self.go_to_search(None)
    
    def close(self):
        """
        关闭窗口
        """
        self.index=None
        self.text.tag_remove('found','1.0','end')
        self.withdraw()
    
    def show(self):
        """
        显示窗口
        """
        self.deiconify()
        self.entry_search.focus_set()


class AboutWindow(Toplevel):
    #TinText的关于窗口
    def __init__(self,version):
        """
        初始化，创建关于窗口
        """
        super().__init__()
        self.title(f'关于 TinText v{version} 应用组')
        self.withdraw()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        center_x = int(screen_width / 2 - 500 / 2)
        center_y = int(screen_height / 2 - 500 / 2)
        self.geometry(f"500x500+{center_x}+{center_y}")
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.tinui=BasicTinUI(self)
        self.tinui.pack(expand=True,fill='both')
        self.tinuixml=TinUIXml(self.tinui)
        with open('./pages/about.xml','r',encoding='utf-8') as f:
            xml=f.read()
        self.tinuixml.loadxml(xml)
    
    def close(self):
        """
        关闭窗口
        """
        self.withdraw()
    
    def show(self):
        """
        显示窗口
        """
        self.deiconify()
    