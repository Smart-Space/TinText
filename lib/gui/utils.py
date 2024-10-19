"""
/lib/gui/utils.py
TinText界面功能中的杂项功能
"""
from tkinter import CallWrapper, Text, Toplevel
import tkinter as tk
from tkinter import ttk
# import ctypes
import os
from threading import Thread, Timer
from time import sleep
import webbrowser
from urllib.request import quote

from tinui import BasicTinUI, TinUIXml, show_error

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


# def TkS(value) -> float:
#     # 高分辨率效果
#     ScaleFactor=ctypes.windll.shcore.GetScaleFactorForDevice(0)
#     if DPI_MODE <= 1:
#         return value
#     elif DPI_MODE == 2:
#         return ScaleFactor/100*value


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
        self.withdraw()
        self.iconbitmap('./logo.ico')
        self.geometry("375x60")# y search 60, replace 125
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


class ReaderWebFinder(Toplevel):
    #TinReader的网页查找器
    def __init__(self,webentryval,*args,**kw):
        """
        初始化，创建网络搜索器
        """
        super().__init__(*args,**kw)
        self.title('网络搜索器')
        self.withdraw()
        self.iconbitmap('./logo.ico')
        self.geometry('375x120')
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.close)

        self.tinui=BasicTinUI(self)
        self.tinui.pack(expand=True,fill='both')

        self.tinuixml=TinUIXml(self.tinui)
        with open('./pages/reader_web_finder.xml','r',encoding='utf-8') as f:
            xml=f.read()
        self.tinuixml.funcs.update({'go_to_search':self.go_to_search,'sel_engine':self.sel_engine})
        self.tinuixml.loadxml(xml)
        self.entry_search=self.tinuixml.tags['entry_search'][0]
        self.webentry=self.tinuixml.tags['webentry'][0]
        
        #从设置文件中获取的自定义搜索引擎
        #新的自定义搜索引擎在搜索后才写入到配置文件中
        self.webentry.insert(0,webentryval)

        self.engine='Bing(默认)'
        self.engines={
            'Bing(默认)':'https://cn.bing.com/search?q=',
            '百度':'https://www.baidu.com/s?wd=',
            '360':'https://www.so.com/s?q=',
            'Google':'https://www.google.com/search?q=',
            '搜狗':'https://www.sogou.com/web?query=',
            '自定义':webentryval,
        }
        self.webentryval=webentryval

        self.entry_search.bind('<Return>',self.go_to_search)
    
    def go_to_search(self,e):
        """
        跳转到搜索
        """
        #如果是自定义，写入到配置文件中
        if self.engine=='自定义':
            url=self.webentry.get()
            if url=='':
                show_error(self,'错误','请输入自定义搜索引擎')
                return
            if url != self.webentryval:
                process.config('set','general','ReaderSearchMode','webengine',url)
                process.config('save','general')
                self.engines[self.engine]=url
                self.webentryval=url
        content=self.entry_search.get()
        content=quote(content)
        webbrowser.open(self.engines[self.engine]+content)
    
    def sel_engine(self,name):
        """
        选择引擎
        """
        self.engine=name

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
        self.iconbitmap('./logo.ico')
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


class WriterHtmlInputer(Toplevel):
    #TinWriter的html输入窗口
    def __init__(self,editor):
        """
        初始化，创建html输入窗口
        """
        super().__init__()
        self.title('HTML输入')
        self.withdraw()
        self.iconbitmap('./logo.ico')
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        center_x = int(screen_width / 2 - 500 / 2)
        center_y = int(screen_height / 2 - 355 / 2)
        self.geometry(f"500x355+{center_x}+{center_y}")
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.close)
        
        self.text=ScrolledText(self,font=('微软雅黑',12),borderwidth=0,relief='flat')
        self.text.place(x=0,y=0,width=500,height=320)

        self.tinui=BasicTinUI(self)
        self.tinui.place(x=0,y=320,width=500,height=35)
        self.tinui.add_paragraph((5,5),text='输入HTML代码以插入TinML格式代码到编辑器中')
        self.tinui.add_button2((495,15),text='插入至编辑器',anchor='e',command=self.inserthtml)
        
        self.editor=editor
    
    def inserthtml(self,e):
        """
        插入html代码到编辑器中
        """
        texts=self.text.get('1.0','end-1c').split('\n')
        self.editor.insert('insert',f'<html>{texts[0]}')
        if len(texts)==1:
            return
        else:
            self.editor.insert('insert',';')
        for text in texts[1:]:
            self.editor.insert('insert',f'\n|{text}')
        self.editor.insert('insert','|\n')
    
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


class WriterTabInputer(Toplevel):
    #TinWriter的表格输入窗口
    def __init__(self,editor):
        """
        初始化，创建标签输入窗口
        """
        super().__init__()
        self.title('表格输入')
        self.withdraw()
        self.iconbitmap('./logo.ico')
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        center_x = int(screen_width / 2 - 500 / 2)
        center_y = int(screen_height / 2 - 500 / 2)
        self.geometry(f"500x500+{center_x}+{center_y}")
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.close)

        self.canvas=tk.Canvas(self,borderwidth=0,relief='flat')
        self.canvas.place(x=0,y=0,width=500,height=450)

        self.tinui=BasicTinUI(self)
        self.tinui.place(x=0,y=450,width=500,height=50)
        with open('./pages/writer-tabinputer.xml','r',encoding='utf-8') as f:
            xml=f.read()
        self.tinuixml=TinUIXml(self.tinui)
        self.tinuixml.funcs['set_table']=self.set_table
        self.tinuixml.loadxml(xml)
        self.entry1=self.tinuixml.tags['entry1'][0]#entry widget
        self.entry2=self.tinuixml.tags['entry2'][0]
        
        self.editor=editor

        self.draw_table()
        
    def show(self):
        """
        显示窗口
        """
        self.deiconify()
    
    def close(self):
        """
        关闭窗口
        """
        self.withdraw()
    
    def draw_table(self):
        #绘制表格选择区域
        #画布界面500x450，每个表格矩形10x10，间隔2
        #留宽5，留高4
        #36行 39列
        y=4
        x=5
        self.tabs_location=dict()#表格->位置
        self.ylocation_tabs=dict()#行位置->表格
        self.xlocation_tabs=dict()#列位置->表格
        for line in range(36):
            self.ylocation_tabs[line+1]=list()
            for i in range(39):
                x+=12
                tab=self.canvas.create_rectangle(x,y,x+10,y+10,fill='grey',width=0)
                self.tabs_location[tab]=(line+1,i+1)
                if i+1 not in self.xlocation_tabs:
                    self.xlocation_tabs[i+1]=list()
                self.xlocation_tabs[i+1].append(tab)
                self.ylocation_tabs[line+1].append(tab)
                self.canvas.tag_bind(tab,'<Enter>',lambda e,item=tab:self.mouse_in(item))
                self.canvas.tag_bind(tab,'<Leave>',lambda e,item=tab:self.mouse_out(item))
                self.canvas.tag_bind(tab,'<Button-1>',lambda e,item=tab:self.mouse_click(item))
            y+=12
            x=5
    
    def mouse_in(self,tab):
        #鼠标在表格上
        x,y=self.tabs_location[tab]
        for line in range(y):
            for tab in self.xlocation_tabs[line+1][:x]:
                self.canvas.itemconfig(tab,fill='lightgrey')
    
    def mouse_out(self,tab):
        #鼠标离开表格上
        x,y=self.tabs_location[tab]
        for line in range(y):
            for tab in self.xlocation_tabs[line+1][:x]:
                self.canvas.itemconfig(tab,fill='grey')

    def mouse_click(self,tab):
        #鼠标点击表格
        x,y=self.tabs_location[tab]
        self.entry1.delete(0,'end')
        self.entry1.insert(0,str(y))#列数
        self.entry2.delete(0,'end')
        self.entry2.insert(0,str(x))#行数
    
    def set_table(self,e):
        #输出表格
        xnum=self.entry1.get()
        ynum=self.entry2.get()
        try:
            xnum=int(xnum)
            ynum=int(ynum)
        except:
            return
        for _ in range(ynum):#行数
            self.editor.insert('insert',f'<tb>{"|".join([" "]*xnum)}\n')
        self.editor.insert('insert',f'</tb>\n')


class WriterCodeInputer(Toplevel):
    #TinWriter的代码输入窗口
    def __init__(self,editor):
        """
        初始化，创建标签输入窗口
        """
        super().__init__()
        self.title('代码输入')
        self.withdraw()
        self.iconbitmap('./logo.ico')
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        center_x = int(screen_width / 2 - 500 / 2)
        center_y = int(screen_height / 2 - 500 / 2)
        self.geometry(f"500x500+{center_x}+{center_y}")
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.close)

        self.text=ScrolledText(self,font=('微软雅黑',12),borderwidth=0,relief='flat')
        self.text.place(x=0,y=0,width=500,height=460)

        self.tinui=BasicTinUI(self)
        self.tinui.place(x=0,y=460,width=500,height=40)
        with open('./pages/writer-codeinputer.xml','r',encoding='utf-8') as f:
            xml=f.read()
        self.tinuixml=TinUIXml(self.tinui)
        self.tinuixml.funcs['set_code']=self.set_code
        self.tinuixml.loadxml(xml)
        self.entry=self.tinuixml.tags['entry'][0]

        self.editor=editor
    
    def set_code(self,e):
        #插入TinML <code>
        code_type=self.entry.get()
        if code_type=='':
            #代码名称为空，不通过
            return
        self.editor.insert('insert',f'<code>{code_type};')
        codes=self.text.get('1.0','end-1c')
        for code in codes.split('\n'):
            self.editor.insert('insert',f'\n|{code.replace("|","%VEB%")}')
        self.editor.insert('insert','|')
    
    def show(self):
        """
        显示窗口
        """
        self.deiconify()
    
    def close(self):
        """
        关闭窗口
        """
        self.withdraw()


#TinWriter编辑框提示部件（非控件，而是接管editor和tintext提示文本框）
class WriterHelper:
    #内部启用多线程，防止阻塞主线程
    ON=True#是否启用提示功能
    infoshow=False#是否显示提示信息
    docsdir='./data/tinfile/docs/'

    #同名信息
    rel_tag_name={
        '<ac>':'<ac>', '<anchor>':'<ac>',
        '<code>':'<code>',
        '<fl>':'<fl>', '<follow>':'<fl>',
        '<html>':'<html>',
        '<img>':'<img>', '<image>':'<img>',
        '<lnk>':'<lnk>', '<link>':'<lnk>', '<a>':'<lnk>',
        '<ls>':'<ls>', '<list>':'<ls>',
        '<n>':'<n>', '<note>':'<n>',
        '<nl>':'<nl>', '<numlist>':'<nl>',
        '<p>':'<p>',
        '<pages>':'<pages>', '</page>':'<pages>', '</pages>':'<pages>',
        '<part>':'<part>', '<pt>':'<part>', '</pt>':'</part>', '</part>':'</part>',
        '<sp>':'<sp>','<separate>':'<sp>',
        '<stop>':'<stop>',
        '<tb>':'<tb>', '<table>':'<tb>', '</tb>':'</tb>', '</table>':'</tb>',
        '<title>':'<title>', '<t>':'<title>',
        '<wait>':'<wait>','<w>':'<wait>',
    }
    
    #alt+g 自动生成的根据
    tags_generate={
    '<ac>':'(#)name',
    '<anchor>':'(#)name',
    '<code>':'type;\n|code1\n|code2\n|code3...|',
    '<fl>':'',
    '<follow>':'',
    '<html>':'html1;\n|html2\n|html3...|',
    '<img>':'name|[url]|[size]',
    '<image>':'name|[url]|[size]',
    '<lnk>':'text|[url]|[description]',
    '<link>':'text|[url]|[description]',
    '<ls>':'list1;\n|list2\n|list3...|',
    '<list>':'list1;\n|list2\n|list3...|',
    '<a>':'text|[url]|[description]',
    '<n>':'note1;\n|[note2]\n|[note3]...|',
    '<note>':'note1;\n|[note2]\n|[note3]...|',
    '<nl>':'list1;\n|list2\n|list3...|',
    '<numlist>':'list1;\n|list2\n|list3...|',
    '<p>':'text1|[text2]|[text3]...',
    '<pages>':'name1|name2|[name3]...',
    '</page>':'',
    '</pages>':'',
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
    '<wait>':'content',
    '<w>':'content',
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
        self.thread.setDaemon(True)
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