"""
/lib/gui/reader.py
主要为TinText的窗口，即TinReader

设计上的TinText应用的主窗口、主进程
"""
from tkinter import Toplevel
from tkinter.filedialog import askopenfilename, asksaveasfilename
import os
import webbrowser

import html2text
from tinui import BasicTinUI, TinUIXml, show_info, show_success, show_warning, show_error, show_question,\
    ask_string

import process
import lib.gui.utils as utils
from lib.TinEngine import TinText
from lib.TinEngine.tin2html import TinTranslator

from lib.structure.makeengine import TinpMakeEngine, TinxMakeEngine

filename=None
tintype='TIN'

def start(_quit,**functions):
    #启动&初始化
    global quit, writerfuncs, makerfuncs
    quit=_quit
    writerfuncs=functions['writerfuncs']
    makerfuncs=functions['makerfuncs']
    __start()

def start_with_file(_filename,_quit,**functions):
    #加载文件启动
    global filename, quit, writerfuncs, makerfuncs
    filename=_filename
    quit=_quit
    writerfuncs=functions['writerfuncs']
    makerfuncs=functions['makerfuncs']
    __start()

def load_tinfile():
    #载入tin文件
    root.focus_set()
    if filename==None:
        return
    if tintype=='TIN':
        with open(filename,encoding='utf-8') as f:
            tincont=f.read()
        title_filename=os.path.basename(filename)
        root.title(f'TinReader - {title_filename}')
        tintext.thread_render(tincont)
    elif tintype=='TINP':
        title_filename=os.path.basename(filename)
        root.title(f'TinReader - {title_filename}')
        key=ask_string(root,'TINP文件','请输入TINP文件的密码')
        if not key:
            return
        with open(filename,'r',encoding='utf-8',errors='surrogatepass') as f:
            tinpcont=f.read()
        tinpmake=TinpMakeEngine(tinpcont)
        tincont=tinpmake.decrypt(key)
        tintext.thread_render(tincont)
    elif tintype=='TINX':
        title_filename=os.path.basename(filename)
        root.title(f'TinReader - {title_filename}')
        key=ask_string(root,'TINX文件','请输入TINX文件的密码')
        if not key:
            return
        tinx=TinxMakeEngine(filename,None)
        tincont=tinx.decrypt(key)
        tintext.thread_render(tincont)


#以下为菜单功能
#文件
def openfile(e):#打开文件
    global filename, tintype
    tinfile=askopenfilename(title='选择文件进行阅读',filetype=[('Tin文件','*.tin;*.tinp;*.tinx')])
    if tinfile:
        if tinfile.endswith('.tin'):
            filename=tinfile
            tintype='TIN'
            load_tinfile()
        elif tinfile.endswith('.tinp'):
            filename=tinfile
            tintype='TINP'
            load_tinfile()
        elif tinfile.endswith('.tinx'):
            filename=tinfile
            tintype='TINX'
            load_tinfile()

def reopenfile(e):#重载当前文件
    load_tinfile()

def open_writer(e):#打开编辑器
    if filename==None:#如果没有打开文件，则不允许打开编辑器
        return
    if tintype=='TINP':
        show_info(root,'TINP文件','无法打开编辑器，因为当前文件为TINP文件')
        return
    elif tintype=='TINX':
        show_info(root,'TINX文件','无法打开编辑器，因为当前文件为TINX文件')
        return
    writerfuncs.start(filename,reopenfile,root)

def quitreader(e):
    quit()

#搜索
def open_textfinder(e):#打开文本查找器
    textfinder.show()

#工具
def outputhtml(e):#导出为HTML
    #鼠标转为等待样式
    #打开data/render/blubook.css读取内容
    #转译成html
    #弹窗提示导出成功
    #鼠标恢复样式
    newname=asksaveasfilename(title='导出为HTML',filetypes=[('html文件','*.html')])
    if not newname:
        return
    if not newname.endswith('.html'):
        newname+='.html'
    root.config(cursor='watch')
    with open('./data/render/blubook.css','r',encoding='utf-8') as f:
        style=f.read()
    tintra=TinTranslator(tintext.tinml)
    try:
        res=tintra.tohtml(_style=style)
        with open(newname,'w',encoding='utf-8') as f:
            f.write(res.render())
        show_success(root,'导出成功','已在指定位置生成HTML文件')
    except Exception as e:
        show_error(root,'导出失败',f'HTML格式导出出现错误：\n{e}')
    finally:
        root.config(cursor='arrow')

def outputmarkdown(e):#导出为Markdown
    #鼠标转为等待样式
    #转译为html
    #转译为markdown
    #弹窗提示导出成功
    #鼠标恢复样式
    newname=asksaveasfilename(title='导出为Markdown',filetypes=[('markdown文件','*.md')])
    if not newname:
        return
    if not newname.endswith('.md'):
        newname+='.md'
    root.config(cursor='watch')
    tintra=TinTranslator(tintext.tinml)
    try:
        res=tintra.tohtml()
        # markdown=tintra.tomarkdown()
    except Exception as e:
        show_error(root,'导出失败(html转译失败)',f'Markdown格式导出出现错误：\n{e}')
    finally:
        root.config(cursor='arrow')
    markdown=html2text.html2text(res.body.render())
    with open(newname,'w',encoding='utf-8') as f:
        f.write(markdown)
    show_success(root,'导出成功','已在指定位置生成Markdown文件')

def open_maker(e):#打开TinMaker
    if filename==None:#如果没有打开文件，则不允许打开编辑器
        show_info(root,'TinMaker','请先打开文件')
        return
    if tintype=='TINP':
        show_error(root,'TINP文件','TINP文件无法被循环加密，无法使用TinMaker')
        return
    elif tintype=='TINX':
        show_error(root,'TINX文件','TINX文件无法替换，无法使用TinMaker')
        return
    makerfuncs.start(filename)

#关于
def open_aboutwindow(e):#打开关于窗口
    aboutwindow.show()

def check_newversion(e):#检查新版本
    root.config(cursor='watch')
    version=process.version('check')
    nowversion=process.config("get","general","Version","ver")
    root.config(cursor='arrow')
    show_info(root,'版本检测',f'当前版本：{nowversion}\n最新版本：{version}')

def open_releas_page(e):#打开发布页面
    process.version('update')


#以下为初始化
def __start():
    global root, tinui, tintext, textfinder, aboutwindow

    root=Toplevel()
    root.title('TinReader')
    root.focus_set()
    root.protocol("WM_DELETE_WINDOW", quit)
    root.withdraw()

    root.iconbitmap('logo.ico')
    root.geometry("700x750")
    root.resizable(width=False, height=False)
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    center_x = int(screen_width / 2 - 700 / 2)
    center_y = int(screen_height / 2 - 750 / 2)
    root.geometry(f"+{center_x}+{center_y-30}")
    root.update()

    menu_file=(
        ('打开\tctrl+o',openfile),
        ('重载\tctrl+r',reopenfile),
        ('编辑\tctrl+e',open_writer),
        '-',
        ('退出\tctrl+q',quitreader)
    )
    menu_search=(
        ('搜索\tctrl+f',open_textfinder),
    )
    menu_tools=(
        ('导出为html',outputhtml),
        ('导出为markdown',outputmarkdown),
        ('-'),
        ('TinMaker',open_maker)
    )
    menu_about=(
        ('关于TinText',open_aboutwindow),
        ('检测新版本',check_newversion),
        '-',
        ('项目主页',lambda e: webbrowser.open('https://tintext.smart-space.com.cn/')),
        ('开发主页',lambda e: webbrowser.open('https://github.com/Smart-Space/TinText')),
        ('发布页面',open_releas_page),
    )

    tinui=BasicTinUI(root,height=30,bg='#fbfbfb')
    tinui.pack(fill='x')
    tinuix=TinUIXml(tinui)
    tinuix.datas.update({'menu_file':menu_file,'menu_search':menu_search,'menu_tools':menu_tools,'menu_about':menu_about})
    tinuix.loadxml(open('pages/reader.xml',encoding='utf-8').read())
    root.update()

    tintext=TinText(root,font='微软雅黑 12')
    tintext.pack(fill='both',expand=True)
    tintext.config(state='disabled')

    root.update()
    root.bind('<Control-o>',openfile)
    root.bind('<Control-r>',reopenfile)
    root.bind('<Control-q>',quitreader)
    root.bind('<Control-e>',open_writer)
    root.bind('<Control-f>',open_textfinder)

    #获取配置信息
    version=process.config('get','general','Version','ver')
    if version in ('',None):
        show_warning(root,'配置文件缺损','无法获取版本号：general[Version][ver]')
        version='未知版本'
    searchmode=process.config('get_item','general','ReaderSearchMode')

    textfinder=utils.TextFinder('TinReader搜索',tintext,searchmode,'ReaderSearchMode')
    aboutwindow=utils.AboutWindow(version)

    root.deiconify()
    load_tinfile()
