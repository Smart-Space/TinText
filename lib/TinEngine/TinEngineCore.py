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
import io
import re
import threading
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED
from tempfile import NamedTemporaryFile

from tkinterweb.htmlwidgets import HtmlFrame
from PIL import Image,ImageTk# require
import requests# tkinterweb require
from TinUI import BasicTinUI

from .tin2html import TinML
from .error import NoLinesMode, TagNoMatch, NoLinesMark, AlreadyStartLine
from .controls import Balloon, TinTextSeparate, TinTextNote


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
        self.tinml=TinML()#tin标记记录
        self.tinparser=TinParser()#解析器
        self.balloon=Balloon()#提示框
        self.img_thread_pool=ThreadPoolExecutor(max_workers=10)#图片下载线程池
        self.__initialize()

    def __initialize(self):
        #内部控件
        self.widgets=list()
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
        #图片，存放图片（ImageTK.PhotoImage）对象的字典
        self.images=dict()
        
    def __render_err(self,msg,index='end'):
        self.insert(index,msg,'error')

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
            index=self.index('end-1c')
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
        self.tag_bind(tag_name,'<Enter>',lambda e:self.balloon.show(e,description))
        self.tag_bind(tag_name,'<Leave>',lambda e:self.balloon.hide(e))
        self.insert('end','\n')

    def __render_separate(self,color='#545965'):
        #分割线
        self.update()
        width=self.winfo_width()
        separator=TinTextSeparate(self,width,color)
        self.widgets.append(separator)
        self.window_create('end',window=separator,align='center')
        self.insert('end','\n')
    
    def __render_image(self,mark,img_file,need_download=True,url='',img_size=None):
        #图片
        #发生错误则返回错误提示文本
        if need_download:
            try:
                res=requests.get(url)
            except Exception as err:
                # print(err)
                return str(err)
            if img_file=='':#空名，直接获取二进制数据
                img=Image.open(io.BytesIO(res.content))
            else:#存在文件（包括后缀），保存到本地
                with open('./data/imgs/'+img_file,'wb') as f:
                    f.write(res.content)
                img=Image.open('./data/imgs/'+img_file)
        else:
            img=Image.open('./data/imgs/'+img_file)
        if img_size:
            #缩放图片
            try:
                #不能是小数
                img_width,img_height=img_size
                width=self.winfo_width()
                height=self.winfo_height()
                if img_width.endswith('%'):
                    width=int(width*float(img_width[:-1])/100)
                else:
                    width=int(img_width)
                if img_height.endswith('%'):
                    height=int(height*float(img_height[:-1])/100)
                else:
                    height=int(img_height)
            except ValueError as e:
                #传值错误，忽略，没有人会蠢到给尺寸传非数字
                # print(e)
                pass
            img=img.resize((width,height))
        self.images[mark]=ImageTk.PhotoImage(img)
        self.image_create(mark,image=self.images[mark])
    
    def __render_note(self,notes):
        #引用说明
        self.update()
        width=self.winfo_width()
        note=TinTextNote(self,width,notes,self.cget('font'),'#5969e0','#7e7e7e',self.cget('background'),'#f9f9f9')
        self.widgets.append(note)
        self.window_create('end',window=note,align='center')
        self.insert('end','\n')

    def render(self,tintext='<tin>TinText',new=True):
        #渲染tin标记
        self.RENDERING=True
        img_threadings=list()
        tinconts=self.tinparser.parse(tintext)
        # self.__load_imgs(imgs)
        self.config(state='normal')
        if new:#新的渲染任务
            self.delete(1.0,'end')#删除内容
            self.images.clear()#清空图片列表
            self.tinml.clear()#删除标记
            for i in self.widgets:
                i.destroy()
            self.widgets.clear()#删除内部控件
            for i in self.tag_names():
                #仅删除开头为“"”的样式名称
                #在TinText渲染中，"tagname"为子样式
                if i[0]=='"':
                    self.tag_delete(i)
            self.mark_unset()#删除所有标记
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
                    self.tinml.addtin('<sp>',color=color)
                case '<img>'|'<image>':
                    #<img>filename|[url]|[size(width x height)]
                    # TinText的图片渲染逻辑与旧版TinText-v3不同，
                    # 记录当前位置，传递给渲染函数，
                    # 再通过线程池下载图片，
                    # 下载完毕后在指定位置插入图片，
                    # 若下载图片失败，则返回错误信息（后期可能改为“破损”图片），也删除mark
                    # 关于size参数，有“x”在其中，判断是否为width%xheight%或widthxheight；
                    # 若没有“X”，则判断是否有“%”，按照等比缩放进行渲染。
                    img_file=unit[2]
                    img_path_name,img_type=os.path.splitext(img_file)
                    img_mark='imgmark'+str(id(unit))
                    img_url=''
                    img_size=None
                    WEBIMAGE=False#是否为网络图片
                    self.insert('end',' ')
                    if unit_length>5:
                        err=f'[{unit[0]}]<img>标记参数超出限制:\n{"|".join(unit[1:])}\n<img>文件名|[网址]|[尺寸]'
                        self.__render_err(err)
                        break
                    #插入标记，给图片占位，继续渲染
                    self.mark_set(img_mark,self.index('end-2c'))
                    # img_mark=self.index('end-1c')
                    if unit_length==3:
                        #只存在文件名，不存在网址
                        if img_path_name=='':
                            #只存在文件名时，不能为空
                            err=f'[{unit[0]}]<img>只含文件名时，文件名不能为空'
                            self.__render_err(err)
                            break
                        elif img_type=='':
                            err=f'[{unit[0]}]<img>只含文件名时，后缀名不能为空'
                            self.__render_err(err)
                            break
                        if not os.path.isfile('./data/imgs/'+img_file):
                            #图片文件不存在
                            err=f'[{unit[0]}]<img>未知图片：{img_file}'
                            self.__render_err(err)
                            break
                    if unit_length>=4:
                        #url存在
                        img_url=unit[3]
                        if img_url=='':
                            #网址不能为空
                            err=f'[{unit[0]}]<img>网址不能为空'
                            self.__render_err(err)
                            break
                        #先判断文件是否存在
                        if os.path.isfile('./data/imgs/'+img_file):
                            #文件存在，则用现有文件
                            WEBIMAGE=False
                        else:
                            #文件不存在，则开启下载
                            WEBIMAGE=True
                    if unit_length>=5:
                        #尺寸存在
                        img_size=unit[4]
                        if img_size=='':
                            err=f'[{unit[0]}]<img>尺寸不能为空：{img_size}'
                            self.__render_err(err)
                            return
                        x_num_check=img_size.count('x')#x的数量
                        if x_num_check!=1:
                            err=f'[{unit[0]}]<img>尺寸格式错误：{img_size}\n<img>的尺寸格式应为：width(%) x height(%)'
                            self.__render_err(err)
                            return
                        img_size=img_size.split('x')
                        img_size[0]=img_size[0].strip()
                        img_size[1]=img_size[1].strip()
                        if 1<=img_size[0].count('%')!=1 and not img_size[0].endswith('%'):
                            err=f'[{unit[0]}]<img>尺寸格式错误：{img_size}\n<img>的宽度格式应为：width(%)或width'
                            self.__render_err(err)
                            return
                        elif 1<=img_size[1].count('%')!=1 and not img_size[1].endswith('%'):
                            err=f'[{unit[0]}]<img>尺寸格式错误：{img_size}\n<img>的高度格式应为：height(%)或height'
                            self.__render_err(err)
                            return
                    img_threading=self.img_thread_pool.submit(self.__render_image,img_mark,img_file,WEBIMAGE,img_url,img_size)
                    img_threadings.append(img_threading)
                    self.tinml.addtin('<img>',filename=img_file,url=img_url,size=img_size)
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
                        description=unit[4]
                    if description=='':
                        description=unit[3]
                    self.__render_link(text,unit[3],description)
                    self.tinml.addtin('<lnk>',text=text,url=unit[3],description=description)
                case '<n>'|'<note>':
                    #<note>note1|[note2]|...
                    #解释说明卡片，构造上与<p>相同
                    #提示符|#5969e0，文本背景(整行)#f9f9f9，文本颜色#7e7e7e
                    self.__render_note(unit[2:])
                    self.tinml.addtin('<note>',note=unit[2:])
                case '<stop>':
                    #<stop>time
                    #暂停渲染，time为秒
                    if unit_length>3:
                        err=f'[{unit[0]}]<stop>标记参数超出限制:\n{"|".join(unit[1:])}\n<stop>时间'
                        self.__render_err(err)
                        break
                    t=unit[2]
                    try:
                        t=float(t)
                    except ValueError:
                        err=f'[{unit[0]}]<stop>时间错误：\n{"|".join(unit[1:])}\n时间需要整数或小数'
                        self.__render_err(err)
                        break
                    if t<=0:
                        err=f'[{unit[0]}]<stop>时间错误：\n{"|".join(unit[1:])}\n时间需要大于0'
                        self.__render_err(err)
                        break
                    #这类只在tin语言渲染中存在的操作，不参与tinml和html渲染
                    sleep(t)
                case '<tb>'|'<table>':
                    #table
                    ...
                case _:
                    err=f"[{unit[0]}]错误标记：{unit[1]}"
                    self.__render_err(err)
                    break
            self.update()
        wait(img_threadings,return_when=ALL_COMPLETED)
        img_threadings.clear()
        self.config(state='disabled')
        self.RENDERING=False
        print(self.tinml)

    def thread_render(self,tintext='<tin>TinText'):
        #创建一个子线程，渲染tin标记
        if not self.RENDERING:
            thread=threading.Thread(target=self.render,args=(tintext,))
            thread.start()
