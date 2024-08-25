"""
/lib/gui/utils.py
TinText界面功能中的杂项功能
"""
from tkinter import CallWrapper, Text, Toplevel
import tkinter as tk
from tkinter import ttk
import os
from threading import Thread, Timer
from time import sleep

from tinui import BasicTinUI, TinUIXml

import process


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
    _nocase=False
    _loop=False
    _regexp=False
    _replaceall=False

    def __init__(self,title='search',text=None,searchmode=None,searchmodename='',*args,**kw):
        """
        初始化，创建文本查找控件
        """
        super().__init__(*args,**kw)
        self.title(title)
        self.iconbitmap('./logo.ico')
        self.geometry("375x60")# y search 60, replace 125
        self.withdraw()
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.close)

        self.text=text
        self.text.tag_config("found", background="yellow")

        self.searchmode=searchmode
        self.searchmodename=searchmodename

        self.tinui=BasicTinUI(self)
        self.tinui.pack(expand=True,fill='both')

        with open('./pages/_finder.xml','r',encoding='utf-8') as f:
            xml=f.read()
        self.tinuixml=TinUIXml(self.tinui)
        self.tinuixml.funcs.update({'go_to_search':self.go_to_search,'go_to_replace':self.go_to_replace,
        'set_case':self.set_case,'set_regexp':self.set_regexp,'set_loop':self.set_loop,
        'set_replaceall':self.set_replaceall,'exchange_word':self.exchange_word})
        self.tinuixml.loadxml(xml)
        self.entry_search=self.tinuixml.tags['entry_search'][0]
        self.entry_replace=self.tinuixml.tags['entry_replace'][0]
        self.check_case_btn=self.tinuixml.tags['check_case_button'][-2]
        self.check_regexp_btn=self.tinuixml.tags['check_regexp_button'][-2]
        self.check_loop_btn=self.tinuixml.tags['check_loop_button'][-2]
        self.check_replaceall_btn=self.tinuixml.tags['check_replaceall_button'][-2]

        if self.searchmode.getboolean('case'): self.check_case_btn.on()
        if self.searchmode.getboolean('regexp'): self.check_regexp_btn.on()
        if self.searchmode.getboolean('loop'): self.check_loop_btn.on()
        if 'replace_all' in self.searchmode:
            if self.searchmode.getboolean('replace_all'): self.check_replaceall_btn.on()

    def go_to_search(self,e):
        """
        查找文本
        """
        self.text.tag_remove('found','1.0','end')
        text=self.entry_search.get()
        if text=='':
            return None, None
        index=self.text.search(text,self.index,stopindex='end',nocase=self._nocase,regexp=self._regexp)
        if index:#有搜索结果
            self.index=index+f'+{len(text)}c'
            self.text.tag_add('found',index,f'{index}+{len(text)}c')
            self.text.mark_set('insert',index)
            self.text.see(index)
            return index, len(text)
        else:
            if self.index=='1.0':
                #无匹配，退出搜索
                self.text.tag_remove('found','1.0','end')
                return None, None
            #匹配完毕，查看是否需要循环搜索
            if self._loop:
                self.index='1.0'
                return self.go_to_search(None)
    
    def go_to_replace(self,e):
        """
        替换文本
        """
        text=self.entry_replace.get()
        if text=='':
            return
        index, length=self.go_to_search(None)
        if not index:
            return
        while index!=None:
            self.text.delete(index,f'{index}+{length}c')
            self.text.insert(index,text,'found')
            if self._replaceall:#替换全部
                index, length=self.go_to_search(None)
            else:
                break
    
    def exchange_word(self,e):
        """
        调换输入框文字
        """
        find_word=self.entry_search.get()
        change_word=self.entry_replace.get()
        self.entry_search.delete(0,'end')
        self.entry_search.insert(0,change_word)
        self.entry_replace.delete(0,'end')
        self.entry_replace.insert(0,find_word)
    
    def close(self):
        """
        关闭窗口
        """
        self.index=None
        self.text.tag_remove('found','1.0','end')
        self.withdraw()
    
    def show(self,replace=False):
        """
        显示窗口
        """
        if replace:#包含替换功能
            self.geometry('375x125')
        else:
            self.geometry('375x60')
        self.deiconify()
        self.entry_search.focus_set()
    
    def set_case(self,val):
        self._nocase=not val
        process.config('set','general',self.searchmodename,'case',str(val))
        process.config('save','general')
    def set_regexp(self,val):
        self._regexp=val
        process.config('set','general',self.searchmodename,'regexp',str(val))
        process.config('save','general')
    def set_loop(self,val):
        self._loop=val
        process.config('set','general',self.searchmodename,'loop',str(val))
        process.config('save','general')
    def set_replaceall(self,val):
        self._replaceall=val
        process.config('set','general',self.searchmodename,'replace_all',str(val))
        process.config('save','general')


class AboutWindow(Toplevel):
    #TinText的关于窗口
    def __init__(self,version):
        """
        初始化，创建关于窗口
        """
        super().__init__()
        self.title(f'关于 TinText v{version} 应用组')
        self.iconbitmap('./logo.ico')
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


#TinWriter编辑框提示部件（非控件，而是接管editor和tintext提示文本框）
class WriterHelper:
    #内部启用多线程，防止阻塞主线程
    ON=True#是否启用提示功能
    infoshow=False#是否显示提示信息
    docsdir='./data/tinfile/docs/'

    #同名信息
    rel_tag_name={
        '<img>':'<img>', '<image>':'<img>',
        '<lnk>':'<lnk>', '<link>':'<lnk>', '<a>':'<lnk>',
        '<n>':'<n>',' <note>':'<n>',
        '<p>':'<p>',
        '<pt>':'<pt>', '<part>':'<pt>', '</pt>':'</pt>', '</part>':'</pt>',
        '<sp>':'<sp>','<separate>':'<sp>',
        '<stop>':'<stop>',
        '<tb>':'<tb>', '<table>':'<tb>', '</tb>':'</tb>', '</table>':'</tb>',
        '<title>':'<title>', '<t>':'<title>',
    }
    
    #alt+g 自动生成的根据
    tags_generate={
    '<img>':'name|[url]|[size]',
    '<image>':'name|[url]|[size]',
    '<lnk>':'text|[url]|[description]',
    '<link>':'text|[url]|[description]',
    '<a>':'text|[url]|[description]',
    '<n>':'note1;\n|[note2]\n|[note3]...|',
    '<note>':'note1;\n|[note2]\n|[note3]...|',
    '<p>':'text1|[text2]|[text3]...',
    '<part>':'name',
    '<pt>':'name',
    '</part>':'name',
    '</pt>':'name',
    '<sp>':'[color]',
    '<separate>':'[color]',
    '<stop>':'time',
    '<tb>':'co1|col2|[col3]...',
    '<table>':'co1|col2|[col3]...',
    '</tb>':'',
    '</table>':'',
    '<title>':'title|[level]',
    '<t>':'title|[level]',
    }

    def __init__(self,editor,about):
        #editor为TinWriter编辑框，about为TinWriter.tintext提示文本框
        self.editor=editor
        self.about=about
        self.info=tk.Label(self.editor,text='',anchor='n',font=self.editor.cget('font'),bg=self.editor.cget('background'),fg='grey',relief='flat')
        self.editor.bind('<Alt-p>',self.edit)
        self.editor.bind('<Alt-g>',self.generate)
        self.editor.bind('<Alt-a>',self.get_tag_doc)
        self.start()
    
    def start(self):
        self.ON=True
        self.thread=Thread(target=self.core)
        self.thread.start()
    
    def core(self):
        #核心函数，负责处理提示
        def __get_char(index):
            #获取index位置的字符
            return index.split('.')[1]
        while self.ON:
            index=self.editor.index('insert')
            line=self.editor.get(f'{index} linestart',f'{index} lineend')
            if __get_char(index)=='0' and line in ('\n',''):#开头
                self.infoshow=True
                lastchar=self.get_last_char()
                if lastchar==None:
                    pass
                elif lastchar=='<':#标签
                    # print('tag')
                    self.showinfo('<>')
                elif lastchar=='|':#多行
                    # print('multi tag')
                    self.showinfo('|')
            else:
                self.infoshow=False
                startchar=self.editor.get(f'{index} linestart')
                if startchar=='<':#标签
                    # print('tag content')
                    ...
                elif startchar=='|':
                    if self.editor.get(f'{index} linestart +1c')=='-':#注释
                        pass
                    else:#多行
                        # print('multi tag content')
                        ...
            sleep(0.3)
            self.info.place_forget()

    def get_last_char(self):
        #获取光标上面几行的第一个有效字符
        #比如 | < 【其它文字】
        char=None
        index=self.editor.index('insert')
        while True:
            if index=='1.0':#开头
                return None
            index=self.editor.index(f'{index} -1l linestart')
            startchar=self.editor.get(index)
            if startchar=='\n':#空行
                continue
            elif startchar=='<':#标签
                if self.editor.get(f'{index} lineend -1c')==';':
                    return '|'
                else:
                    return startchar
            elif startchar=='|':
                if self.editor.get(f'{index} +1c')=='-':#注释
                    continue
                elif self.editor.get(f'{index} lineend -1c')=='|':#多行结束
                    return '<'#当作标签结束
                else:
                    return startchar
            else:
                continue
    
    def showinfo(self,char):
        #显示提示
        self.infoshow=True
        bbox=self.editor.bbox('insert')
        self.info['text']=char
        if not bbox:
            return
        self.info.place(x=bbox[0]+1,y=bbox[1]-4)
    
    def edit(self,e):
        #编辑提示
        # self.editor.delete('insert-1c')
        if not self.infoshow:
            return
        char=self.info['text']
        self.editor.insert('insert',char)
        self.info.place_forget()
        if char=='<>':
            self.editor.mark_set('insert','insert -1c')

    def generate(self,e):
        #生成提示
        if self.editor.get('insert linestart')!='<':#不是标签
            return
        lastchar=self.editor.get('insert lineend')
        if lastchar=='\n':#如果是换行，则检查前一个字符
            if self.editor.get('insert lineend -1c')!='>':#末尾不是标签结尾
                return
        elif lastchar!='>':#最后一行，检查最后一个字符
            return
        tag=self.editor.get('insert linestart','insert lineend')
        if tag not in self.tags_generate:
            return
        else:
            content=self.tags_generate[tag]
            self.editor.insert('insert lineend',content)
    
    def get_tag_doc(self,e):
        #显示标签说明
        if self.editor.get('insert linestart')!='<':#不是标签
            return
        tag_end_pos=self.editor.search('>','insert linestart','insert lineend')
        if not tag_end_pos:
            return
        #获取标签名
        tag_name=self.editor.get('insert linestart',f'{tag_end_pos} +1c')
        if tag_name not in self.rel_tag_name:
            return
        relname=self.rel_tag_name[tag_name]
        doc_file=self.docsdir+f'{relname[1:-1]}.tin'
        if os.path.isfile(doc_file):
            with open(doc_file,'r',encoding='utf-8') as f:
                content=f.read()
            self.about.thread_render(content)