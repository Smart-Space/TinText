"""
/lib/gui/reader.py
主要为TinText的窗口，即TinReader

设计上的TinText应用的主窗口、主进程
"""
from tkinter import Toplevel
from tkinter.filedialog import askopenfile
import os

from TinUI import BasicTinUI, TinUIXml

from lib.TinEngine import TinText
from lib.TinEngine.tin2html import TinTranslator

filename=None


def start(_quit,**functions):
    #启动&初始化
    global quit, writerfuncs
    quit=_quit
    writerfuncs=functions['writerfuncs']
    __start()

def start_with_file(_filename,_quit,**functions):
    #加载文件启动
    global filename, quit, writerfuncs
    filename=_filename
    quit=_quit
    writerfuncs=functions['writerfuncs']
    __start()

def load_tinfile():
    #载入tin文件
    if filename==None:
        return
    with open(filename,encoding='utf-8') as f:
        tincont=f.read()
    title_filename=os.path.basename(filename)
    root.title(f'TinReader - {title_filename}')
    tintext.thread_render(tincont)


#以下为菜单功能
#文件
def openfile(e):#打开文件
    global filename
    tinfile=askopenfile(title='选择文件进行阅读',filetype=[('Tin文件','*.tin;*.tinx')])
    if tinfile:
        if tinfile.endswith('.tin'):
            filename=tinfile
        elif tinfile.endswith('.tinx'):
            ...

def reopenfile(e):#重载当前文件
    load_tinfile()

def open_writer(e):#打开编辑器
    if filename==None:#如果没有打开文件，则不允许打开编辑器
        return
    writerfuncs.start(filename,reopenfile,root)

def quitreader(e):
    quit()

#搜索

#工具
def outputhtml(e):#导出为HTML
    #打开data/render/blubook.css读取内容
    #转译成html
    with open('./data/render/blubook.css','r',encoding='utf-8') as f:
        style=f.read()
    tintra=TinTranslator(tintext.tinml)
    res=tintra.tohtml(_style=style)
    with open('./data/render/blubook.html','w',encoding='utf-8') as f:
        f.write(res.render())


#以下为初始化
def __start():
    global root, tinui, tintext

    root=Toplevel()
    root.title('TinReader')
    root.focus()
    root.protocol("WM_DELETE_WINDOW", quit)

    root.title('TinReader')
    root.geometry("700x750")
    root.resizable(width=False, height=False)
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    center_x = int(screen_width / 2 - 700 / 2)
    center_y = int(screen_height / 2 - 750 / 2)
    root.geometry(f"700x750+{center_x}+{center_y-30}")
    root.update()

    menu_file=(
        ('打开\tctrl+o',openfile),
        ('重载\tctrl+r',reopenfile),
        ('编辑\tctrl+e',open_writer),
        '-',
        ('退出\tctrl+q',quitreader)
    )
    menu_tools=(
        ('导出为html',outputhtml),
    )

    tinui=BasicTinUI(root,height=30,bg='#fbfbfb')
    tinui.pack(fill='x')
    tinuix=TinUIXml(tinui)
    tinuix.datas.update({'menu_file':menu_file,'menu_tools':menu_tools})
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

    load_tinfile()
