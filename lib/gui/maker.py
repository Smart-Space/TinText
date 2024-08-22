"""
/lib/gui/maker.py
TinText的tinp、tinx生成器，即TinMaker
"""
from tkinter import Toplevel
from tkinter.filedialog import asksaveasfilename
import os
import locale

from tinui import BasicTinUI, TinUIXml, show_info, show_success, show_warning, show_error
from lib.structure.makeengine import TinpMakeEngine, TinxMakeEngine

filename=None
MAKE_TYPE=None#要生成的文件类型


def initial(_filename):
    #初始化
    global filename
    if filename:#已经打开过TinMaker
        if _filename!=filename:
            filename=_filename
        show()
    else:
        filename=_filename
        __start()


def log(text):
    #记录log
    tinui.textbox.config(state='normal')
    tinui.textbox.insert('end', text+'\n')
    tinui.textbox.update()
    tinui.textbox.see('end')
    tinui.textbox.config(state='disabled')


def sel_type(tintype):
    global MAKE_TYPE
    MAKE_TYPE=tintype
    if MAKE_TYPE=='TINP (加密)':
        log('已选择[TINP (加密)]')
    elif MAKE_TYPE=='TINX (集成)':
        log('已选择[TINX (集成)]')
        ...#working


def __gen():
    #生成目标类型文件
    key=tinui.entry.get()
    if key=='':
        show_warning(root,'密钥缺失','请输入一个密钥')
        return
    
    if MAKE_TYPE==None:
        show_warning(root,'类型缺失','请选择要生成的文件类型')
        return

    if MAKE_TYPE=='TINP (加密)':
        with open(filename,'r',encoding='utf-8') as f:
            text=f.read()
        #记录文本框log
        log('开始生成TINP文件……')
        tinpmake=TinpMakeEngine(text)
        log('密钥：'+key)
        log('密钥长度：'+str(len(key)))
        log('正在加密……')
        tinptext=tinpmake.encrypt(key)
        if tinptext==None:
            show_error(root,'加密失败','密钥长度必须小于等于文本长度')
            log('加密失败，密钥长度必须小于等于文本长度')
            return
        #获取filename所在的文件夹和文件名(无后缀名)
        filedir=os.path.dirname(filename)+'/'
        name=os.path.splitext(os.path.basename(filename))[0]+'.tinp'
        tinpfile=filedir+name
        log('正在保存TINP文件……')
        with open(tinpfile,'w',encoding='utf-8',errors='surrogatepass') as f:
            f.write(tinptext)
        log('TINP文件已保存至：'+tinpfile)
        log('该TINP解密密码：'+key+'（请妥善保管）')
        #结束记录log
    elif MAKE_TYPE=='TINX (集成)':
        #记录文本框log
        log('开始生成TINX文件……')
        tinxmake=TinxMakeEngine(filename,log)
        log('密钥：'+key)
        log('密钥长度：'+str(len(key)))
        log('正在加密……')
        tinxmake.encrypt(key)
        #获取filename所在的文件夹和文件名(无后缀名)
        filedir=os.path.dirname(filename)+'/'
        name=os.path.splitext(os.path.basename(filename))[0]+'.tinx'
        tinxfile=filedir+name
        log('TINX文件已保存至：'+tinxfile)
        log('该TINX解密密码：'+key+'（请妥善保管）')
        #结束记录log

def gen(e):
    #生成目标类型文件
    tinui.combobox.disable()
    tinui.entry.disable()
    tinui.button.disable()
    __gen()
    tinui.combobox.active()
    tinui.entry.normal()
    tinui.button.active()


def show():
    root.deiconify()
    title_filename=os.path.basename(filename)
    root.title('TinMaker - '+title_filename)
    log('==============================')
    log('当前文件：'+filename)
    log('请选择要生成的文件类型……')

def close():
    root.withdraw()

def __start():
    #创建一个500x500，居中窗口
    global root, tinui
    root=Toplevel()
    root.title('TinMaker')
    root.focus_set()
    root.iconbitmap('./logo.ico')
    root.resizable(False, False)
    root.geometry('500x500')

    root.protocol("WM_DELETE_WINDOW", close)

    screen_width=root.winfo_screenwidth()
    screen_height=root.winfo_screenheight()
    center_x=int(screen_width/2 - 500/2)
    center_y=int(screen_height/2 - 500/2)
    root.geometry('+%d+%d'%(center_x, center_y-20))
    root.update()

    tinui=BasicTinUI(root)
    tinui.pack(fill='both',expand=True)
    tinuix=TinUIXml(tinui)
    tinuix.funcs.update({'sel_type': sel_type, 'gen': gen})
    tinuix.loadxml(open('pages/maker.xml',encoding='utf-8').read())

    tinui.combobox=tinuix.tags['combobox'][-2]#funcs
    tinui.entry=tinuix.tags['entry'][-2]#funcs
    tinui.button=tinuix.tags['button'][-2]#funcs
    tinui.textbox=tinuix.tags['textbox'][0]#widget

    tinui.textbox.config(state='disabled')

    root.update()

    title_filename=os.path.basename(filename)
    root.title('TinMaker - '+title_filename)

    log('TINP文件使用XOR加密，密钥长度必须小于等于文本长度，且安全性与密钥直接挂钩')
    #log('TINX文件...')
    log('==============================')
    log('当前文件：'+filename)
    log('请选择要生成的文件类型……')