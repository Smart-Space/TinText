"""
TinEngine核心类
"""
from tkinter.scrolledtext import ScrolledText
import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showinfo,askyesno,showerror
from tkinter.filedialog import askdirectory
import tkinter.font as tkfont
import webbrowser
from time import sleep
import subprocess
import os
import re
import threading
from tempfile import NamedTemporaryFile

from tkinterweb.htmlwidgets import HtmlFrame
from PIL import Image,ImageTk# require
import requests# tkinterweb require

from .tin2html import TinML
from .error import NoLinesMode, TagNoMatch, NoLinesMark, AlreadyStartLine
from .controls import Balloon, TinTextSeparate


class TinParser():
    """
    tin标记解析模块
    """
    ver='V-4'

    def __init__(self):
        #<tag>, -, |, |-, [空]
        self.tin_re=re.compile('[ ]{0,}(<.*?>|-|\\|-|\\||)(.*)')
        self.tag_start_attrs_tuple=('|','-')
        #特殊标记|，-，;

    def __tran_spec(self,text):
        #特殊标记转义 translate special marks
        # text=text.replace('%SEM%',';')#Semicolon, @SEM@->;
        text=text.replace('%VEB%','|')#Vertical bar, @VEB@->|
        return text

    def parse(self,tin):
        #分析
        TAGATTR=False#标签参数注入，用于多行表达
        line_count=0#行数
        for line in tin.split('\n'):
            line_count+=1
            if line=='':
                continue
            if line.startswith('|-'):
                #注释
                continue
            unit=self.tin_re.match(line)
            if unit==None:#无法匹配
                err=f"无法匹配的tin标记[{line_count}]:\n{line}"
                yield TagNoMatch(err)
                break
            unit=unit.groups()
            if unit[1].endswith(';'):#开启多行表达
                if TAGATTR:
                    err=f"重复使用多行表达标记[{line_count}]:\n{line}\n上方标签的多行表达未结束"
                    yield AlreadyStartLine(err)
                TAGATTR=True
                tagattrs=list()
                tagattrs.append(line_count)
                tagattrs.append(unit[0])
                tagattrs.append(unit[1][:-1])
                continue
            if TAGATTR and (unit[0] not in self.tag_start_attrs_tuple):
                #多行表达标签没有正确的后续标记
                err=f"多行表达错误[{line_count}]:\n{line}\n多行表达缺少结束标记，或者更改上方标签为单行表达\n多行表达开始于[{tagattrs[0]}]"
                yield NoLinesMark(err)
                break
            if unit[0] in self.tag_start_attrs_tuple:#多行表达
                if not TAGATTR:
                    #TAGATTR:False时，提出警告
                    err=f"标记未使用多行表达，但出现了多行表达的参数[{line_count}]:\n{line}\n请检查上方标记参数末尾是否有\";\""
                    yield NoLinesMode(err)
                    break
                if unit[1].endswith('|'):#多行表达结束
                    TAGATTR=False
                    tagattrs.append(unit[1][:-1])
                    yield tuple(tagattrs)
                    del tagattrs
                    continue
                tagattrs.append(unit[1])
                continue
            attrs=unit[1].split('|')
            rattrs=list()#result attrs
            for i in attrs:
                #对已经获得的参数值进行特殊标记文本转义，这可能降低效率，目前没有好的方法
                rattrs.append(i.replace('%VEB%','|'))
            yield line_count,unit[0],*rattrs


class TinText(ScrolledText):
    """
    TinEngine.TinText
    tin标记语言渲染核心
    """
    RENDERING=False#渲染状态

    def __init__(self, master, *args, **kw):
        """
        部分参数是直接确定的
        开发者只能通过实例化后进行更改
        """
        super().__init__(master, *args, **kw)
        self.config(borderwidth=0, relief="flat", insertbackground='#000000', insertborderwidth=1,
            wrap='char', spacing1=10)
        self.tinml=TinML()
        self.tinparser=TinParser()
        self.balloon=Balloon()
        self.__initialize()

    def __initialize(self):
        #自身样式
        #鼠标为箭头
        self.config(cursor='arrow')
        #==========
        #相关设置
        #标题
        font_info=self.cget('font').split(' ')
        self.font_family=font_info[0]
        self.font_size=int(font_info[1])
        self.title_level=('1','2','3','4','5','6')
        self.title_size_dict={'1':self.font_size+12,
            '2':self.font_size+10,
            '3':self.font_size+8,
            '4':self.font_size+6,
            '5':self.font_size+4,
            '6':self.font_size+2
        }
        #文本块开头标记
        self.paragraph_mark=('*','/','_','-','!')
        self.paragraph_link_re=re.compile('.*?!\[(.*?)\]\((..*?)\)')
        #==========
        #基本样式
        #错误信息
        self.tag_config('error',foreground='red')
        #标题，鼠标为输入样式
        self.tag_config('title')
        self.tag_config('title1',font=(self.font_family,self.title_size_dict['1']))
        self.tag_config('title2',font=(self.font_family,self.title_size_dict['2']))
        self.tag_config('title3',font=(self.font_family,self.title_size_dict['3']))
        self.tag_config('title4',font=(self.font_family,self.title_size_dict['4']))
        self.tag_config('title5',font=(self.font_family,self.title_size_dict['5']))
        self.tag_config('title6',font=(self.font_family,self.title_size_dict['6']))
        self.tag_bind('title','<Enter>',lambda e:self.config(cursor='xterm'))
        self.tag_bind('title','<Leave>',lambda e:self.config(cursor='arrow'))
        #普通文本段，各个样式（粗体*、斜体/、下划线_、删除线-、超链接!等）文本段，鼠标为输入样式
        self.tag_config('paragraph')#基础样式，每个都有
        self.tag_bind('paragraph','<Enter>',lambda e:self.config(cursor='xterm'))
        self.tag_bind('paragraph','<Leave>',lambda e:self.config(cursor='arrow'))
        #超链接，鼠标为超链接小手样式
        #对于具体的超链接，tag名为"link-index"
        #该标签为自带换行
        self.tag_config('link',foreground='#006cb4',font=(self.font_family,self.font_size,'underline'))
        self.tag_bind('link','<Enter>',lambda e:self.config(cursor='hand2'))
        self.tag_bind('link','<Leave>',lambda e:self.config(cursor='arrow'))

    def __load_imgs(self,imgs:list):
        #多线程处理图片下载
        #首先判断data/render/imgs有没有同名img
        #若没有，根据网址下载
        print('')
        ...

    def __render_err(self,msg):
        self.insert('end',msg,'error')

    def __render_title(self,title,level):
        #标题
        self.insert('end',title,('title',f'title{level}'))
        self.insert('end','\n')

    def __render_paragraph(self,text,newline=False):
        #普通文本，默认不自动换行
        if text=='':
            pass
        elif text[0]==' ':
            self.insert('end',text[1:],'paragraph')
        elif text[0] not in self.paragraph_mark:
            self.insert('end',text,'paragraph')
        else:
            head_mark=text[:5]
            head_num=0
            p_tags=[]
            if '*' in head_mark:
                head_num+=1
                p_tags.append('bold')
            if '/' in head_mark:
                head_num+=1
                p_tags.append('italic')
            if '_' in head_mark:
                head_num+=1
                p_tags.append('underline')
            if '-' in head_mark:
                head_num+=1
                p_tags.append('overstrike')
            if '!' in head_mark:
                # head_num+=1
                result=self.paragraph_link_re.match(text)
                if result==None:
                    #如果使用了!开头标记但没有遵循![text](url)格式
                    #按普通文本渲染
                    head_num+=1
                else:
                    text,url=result.groups()
                    if text=='':
                        text=url
                    index=self.index('end')
                    tag_name=f'"link-{index}"'
                    if 'underline' not in p_tags:
                        p_tags.append('underline')
                    self.tag_config(tag_name,font=(self.font_family,self.font_size,*p_tags))
                    self.tag_bind(tag_name,'<Button-1>',lambda e:webbrowser.open(url))
                    self.tag_bind(tag_name,'<Enter>',lambda e:self.balloon.show(e,url))
                    self.tag_bind(tag_name,'<Leave>',lambda e:self.balloon.hide(e))
                    self.insert('end',text,('link',tag_name))
                    if newline:
                        self.insert('end','\n')
                    return
            index=self.index('end')
            tag_name=f'"paragraph-{index}"'
            self.tag_config(tag_name,font=(self.font_family,self.font_size,*p_tags))
            self.insert('end',text[head_num:],('paragraph',tag_name))
        if newline:
            self.insert('end','\n')

    def __render_link(self,text,url,description=''):
        #超链接
        index=self.index('end')
        tag_name=f'"link-{index}"'
        self.tag_config(tag_name)
        self.insert('end',text,('link',tag_name))
        self.tag_bind(tag_name,'<Button-1>',lambda e:webbrowser.open(url))
        self.tag_bind(tag_name,'<Enter>',lambda e:self.balloon.show(e,url))
        self.tag_bind(tag_name,'<Leave>',lambda e:self.balloon.hide(e))
        self.insert('end','\n')

    def __render_separate(self,color='#545965'):
        #分割线
        self.update()
        width=self.winfo_width()
        self.window_create('end',window=TinTextSeparate(self,width,color),align='center')
        self.insert('end','\n')

    def render(self,tintext='<tin>TinText',new=True):
        #渲染tin标记
        self.RENDERING=True
        # tinconts,imgs=self.tinparser.parse(tintext)
        tinconts=self.tinparser.parse(tintext)
        # self.__load_imgs(imgs)
        self.config(state='normal')
        if new:#新的渲染任务
            self.delete(1.0,'end')
            self.tinml.clear()
            for i in self.tag_names():
                #仅删除开头为“{”的样式名称
                #在TinText渲染中，{tagname}为子样式
                if i[0]=='"':
                    self.tag_delete(i)
        for unit in tinconts:
            #unit[0]为行数，unit[1]为标记标签，unit[2]必定存在
            #处理错误
            if type(unit)!=tuple:
                self.__render_err(unit.msg)
                break
            #解析标记、渲染
            unit_length=len(unit)
            match unit[1]:
                case '<tin>':
                    #<tin>可认为是注释
                    #理论上应该用作文件描述
                    continue
                case '<p>':
                    #<p>text1|[text2]|...
                    #参数无穷，只在最后一段文本进行换行，适用于<p>内文本样式拼接
                    # 开头标记为空格时，剪去一个空格，因此文本块开头如果需要一个空格时，
                    # 在前一个文本块加入空格，或在该文本快加入两个空格，以此类推
                    for p in unit[2:-1]:
                        self.__render_paragraph(p)
                    self.__render_paragraph(unit[-1],True)
                    #后期引入字形（粗体、下划线、斜体、删除线等）
                    self.tinml.addtin('<p>',text=unit[2:])
                case '':
                    #默认文本，同<p>的第一个参数
                    self.__render_paragraph(''.join(unit[2]),True)
                    self.tinml.addtin('<p>',text=unit[2:])
                case '<title>'|'<t>':
                    #<title>title|[level]
                    #title-标题
                    #level-标题级别，1~6
                    level=''
                    if unit_length>4:
                        err=f'[{unit[0]}]<title>标记参数超出限制:\n{"|".join(unit[1:])}\n<title>标题|级别'
                        self.__render_err(err)
                        break
                    if unit_length>=3:
                        level='1'
                    if unit_length>=4:
                        level=unit[3]
                        if level=='':
                            level='1'
                        elif level not in self.title_level:
                            err=f'[{unit[0]}]<title>标题级别应在1~6中，而非"{level}"'
                            self.__render_err(err)
                            break
                    self.__render_title(unit[2],level)
                    self.tinml.addtin('<title>',title=unit[2],level=level)
                case '<sp>'|'<separate>':
                    #<sp>color
                    #color的值可为空，默认为 #545965
                    color='#545965'
                    if unit_length>3:
                        err=f'[{unit[0]}]<sp>标记参数超出限制:\n{"|".join(unit[1:])}\n<sp>[颜色]'
                        self.__render_err(err)
                        break
                    if unit_length>=3:
                        if unit[2]=='':
                            pass
                        else:
                            color=unit[2]
                    self.__render_separate(color)
                case '<img>':
                    #<img>filename|[url]|[alt]
                    # TinText的图片渲染逻辑与旧版TinText-v3不同，
                    # 先在当前<img>标记渲染位置插入一个mark（通过self.index("end")），
                    # 再通过线程池下载图片，
                    # 下载完毕后在mark位置插入图片，删除mark，
                    # 若下载图片失败，则返回错误信息（后期可能改为“破损”图片）
                    # 关于alt参数，有“x”在其中，判断是否为width%xheight%或widthxheight；
                    # 若没有“X”，则判断是否有“%”，按照等比缩放进行渲染。
                    ...
                    # self.tinml.addtin('<img>',filename=unit[2],url=url,alt=alt)
                case '<lnk>'|'<link>'|'<a>':
                    #<lnk>text|url|[description]
                    #text可为空，则显示url
                    #本标签自带换行，若不想要换行，则使用<p>的!开头标记
                    description=''
                    if unit_length>5:
                        err=f'[{unit[0]}]<lnk>标记参数超出限制:\n{"|".join(unit[1:])}\n<lnk>文本|网址|描述'
                        self.__render_err(err)
                        break
                    if unit_length==3:
                        #只存在文本，不存在网址，标记无效
                        err=f'[{unit[0]}]<lnk>标记参数不足:\n{"|".join(unit[1:])}\n<lnk>文本|网址|[描述]'
                        self.__render_err(err)
                        break
                    if unit_length>=4:
                        #判断url是否存在
                        if unit[3]=='':
                            err=f'[{unit[0]}]<lnk>的网址不能为空:\n{"|".join(unit[1:])}\n<lnk>文本|网址|[描述]'
                            self.__render_err(err)
                            break
                        #判断展示文本是否存在，如果不存在，则显示url
                        if unit[2]=='':
                            text=unit[3]
                        else:
                            text=unit[2]
                    if unit_length>=5:
                        #判断描述是否存在，如果不存在，则显示url
                        if unit[4]=='':
                            description=unit[3]
                        else:
                            description=unit[4]
                    self.__render_link(text,unit[3],description)
                    self.tinml.addtin('<lnk>',text=text,url=unit[3],description=description)
                case '<n>'|'<note>':
                    #<note>note1|[note2]|...
                    #解释说明卡片，构造上与<p>相同
                    #提示符|#5969e0，文本背景(整行)#f9f9f9，文本颜色#7e7e7e
                    ...
                case '<tb>'|'<table>':
                    #table
                    ...
                case _:
                    err=f"[{unit[0]}]错误标记：{unit[1]}"
                    self.__render_err(err)
                    break
            self.update()
        self.config(state='disabled')
        self.RENDERING=False
        print(self.tinml)

    def thread_render(self,tintext='<tin>TinText'):
        #创建一个子线程，渲染tin标记
        if not self.RENDERING:
            thread=threading.Thread(target=self.render,args=(tintext,))
            thread.start()


testtin="""<tin>TinText
<title>title|ascfdf|ss||sddd
<p>xsa;
|scssd
|fdfb|

|-ascvf

dcd

<p>acsc
|ascca

<lnk>ccc|www.markdown.com
"""
