"""
/lib/gui/writer.py
具有*.tin&*.tinx编辑功能的窗口，即TinWriter

设计上作为TinReader的下一级，通过TinReader调用
"""
from tkinter import Toplevel, StringVar
from tkinter.scrolledtext import ScrolledText as Text
from tkinter.messagebox import askyesno
from tkinter.filedialog import asksaveasfilename
import os

from TinUI import BasicTinUI, TinUIXml

import lib.gui.utils as utils
from lib.TinEngine import TinText


already=False#判断是否已经加载过界面，避免重复加载
filename=None
SAVE=True#文件是否已保存

#配色数据(fg,bg)
color_tags=('comment','separate','tag','tag_name')
color_dict={
    'comment':('#6a9955','#ffffff'),#注释
    'separate':('#8a8a8a','#ededed'),#分隔符|，开头的-，结尾的;
    'tag':('#0000ff','#ffffff'),#标签<...>
    'tag_name':('#a31515','#ffffff'),#标签名
}


def start(_filname='',_reopenfunc=None,_readerroot=None):
    #由TinReader调用，加载窗口并显示
    global filename,readerroot,reopenfunc
    #判断是否是新文件，如果是，更新全局filename
    readerroot=_readerroot
    reopenfunc=_reopenfunc
    if filename==_filname:
        pass
    else:
        filename=_filname
    #判断是否已经加载过窗口，避免重复加载
    if already:
        root.deiconify()
        load_tinfile()
    else:
        __start()

def closs_writer():
    #关闭窗口，并保存文件
    #若文件为保存，询问是否保存
    global SAVE
    if SAVE:
        pass
    else:
        if askyesno('该文件未保存','是否在编辑器关闭之前保存该文件？'):
            save_file(None)
    SAVE=True
    root.withdraw()
    readerroot.focus_set()


def load_tinfile():
    #加载文件，并显示在窗口中
    editor.delete('1.0', 'end')
    with open(filename, 'r', encoding='utf-8') as f:
        editor.insert('end', f.read())
    editor.edit_modified(False)
    #...其它渲染操作
    highlight(True)



def save_file(e):
    #从editor中获取内容，并保存到文件
    global SAVE
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(editor.get('1.0', 'end-1c'))#减去结尾换行符
    SAVE=True
    title_filename=os.path.basename(filename)
    root.title('TinWriter - '+title_filename)
    # editor.edit_modified(0)

def saveas_file(e):
    #另存为，保存文件到新位置
    global SAVE,filename
    newname=asksaveasfilename(title='另存为tin文件',filetypes=[('Tin文件','*.tin;*.tinx')])
    if newname:
        if newname.endswith('.tin'):
            with open(newname,'w',encoding='utf-8') as f:
                f.write(editor.get('1.0','end-1c'))
        elif newname.endswith('.tinx'):
            ...


def editor_undo(e):
    #撤销
    try:
        # editor.tk.call(peert, 'configure', '-state', 'normal')
        editor.edit_undo()
        # editor.tk.call(peert, 'configure', '-state', 'disabled')
    except:
        pass

def editor_redo(e):
    #重做
    try:
        # editor.tk.call(peert, 'configure', '-state', 'normal')
        editor.edit_redo()
        # editor.tk.call(peert, 'configure', '-state', 'disabled')
    except:
        pass


def peer_synchronize(e):
    #编辑框和缩略图同步
    # index=editor.index('@375,355')
    # editor.tk.call(peert, 'yview', '-pickplace', index)
    first,end=editor.vbar.get()
    editor.tk.call(peert,'yview','moveto',first)

def editor_synchronize(e):
    #缩略图和编辑框同步
    index=editor.tk.call(peert, 'index', '@0,200')
    editor.yview('-pickplace', index)


def on_text_change(e):
    #接受editor的文本变化事件
    global SAVE
    if editor.edit_modified()==0:
       pass
    else:
        editor.edit_modified(0)
        if SAVE:
            SAVE=False
            title_filename=os.path.basename(filename)
            root.title('TinWriter - *'+title_filename)
        else:
            pass
        highlight()

def __get_index_line(index):
    #返回index所在行号
    return index.split('.')[0]
def __get_index_char(index):
    #返回index所在列号
    return index.split('.')[1]
def highlight(all=False):
    #代码高亮
    if all:#全部高亮
        start='1.0'
        end='end'
    else:#部分高亮
        start=editor.index('insert-50l')
        end=editor.index('insert+50l')
    #清空区域样式
    for tag in color_tags:
        editor.tag_remove(tag, start, end)
    #以下循环匹配，用s代指start
    #分隔符
    s=start
    linemode=False#多行模式
    while True:
        pos=editor.search('[;\|-]', s, end, regexp=True)
        if not pos:
            break
        s=None
        char=editor.get(pos)
        if char==';':
            line_context=editor.get(f"{pos} linestart", f"{pos} lineend")
            if line_context.lstrip()[0]!='<':
                #开头不是标签，则跳过
                s=f"{pos}+1c"
            #如果已经是多行模式，则跳过
            elif linemode:
                s=f"{pos}+1c"
            else:#-1c是为了去除换行符的影响
                line_last=f"{pos} lineend -1c"
                if pos==editor.index(line_last):#判断是否为行末
                    editor.tag_add('separate', pos)
                    linemode=True
                    s=f"{pos}+2c"
                else:
                    s=f"{pos}+1c"
        elif char=='-':
            if linemode:#开启了多行模式
                if __get_index_char(pos)=='0':#开头
                    editor.tag_add('separate', pos)
                    s=f"{pos}+1l"
                else:
                    s=f"{pos}+1c"
            else:
                s=f"{pos}+1c"
        elif char=='|':
            line_context=editor.get(f"{pos} linestart", f"{pos} lineend")
            if linemode:#开启了多行模式
                #判断是不是在行末终止了多行模式
                line_last=f"{pos} lineend -1c"
                if pos==editor.index(line_last):#结尾
                    linemode=False
                    editor.tag_add('separate', pos)
                    s=f"{pos}+2c"
                elif __get_index_char(pos)=='0':#开头
                    editor.tag_add('separate', pos)
                    s=f"{pos} lineend -1c"#跳到行末
            elif line_context.lstrip()[0]!='<':
                #开头不是标签，则跳过
                s=f"{pos}+1l linestart"
            else:
                #判断行末是不是;开启了多行模式
                line_last=f"{pos} lineend -1c"
                if editor.get(line_last)==';':
                    s=f"{pos}+1l linestart"
                else:
                    #若是单行模式，则正常高亮
                    editor.tag_add('separate', pos)
                    s=f"{pos}+1c"
        else:
            s=f"{pos}+1c"
        # if not s: s=f"{pos}+1c"
    #标签
    s=f"{__get_index_line(start)}.0"
    while True:
        start_pos=editor.search('[ ]{0,}<', s, end, regexp=True)
        if not start_pos:
            break
        s=f"{start_pos}+1c"
        end_pos=editor.search('>', s, end, regexp=True)
        if not end_pos:
            #标签未闭合只跳过，不终止
            pass
        else:
            editor.tag_add('tag', start_pos)
            editor.tag_add('tag', end_pos)
            editor.tag_add('tag_name', f"{start_pos}+1c", end_pos)
        start_pos=f"{__get_index_line(start_pos)}.0"
        s=f"{start_pos}+1l"
    #注释
    s=f"{__get_index_line(start)}.0"
    while True:
        pos=editor.search('[ ]{0,}(\|-).*', s, end, regexp=True)
        if not pos:
            break
        pos=f"{__get_index_line(pos)}.0"
        editor.tag_add('comment', pos, f"{pos}+1l-1c")
        s=f"{pos}+1l"
    editor.tag_raise('comment')
    editor.tag_raise('sel')


#防止peer遭到更改，同时便于撤销与重做操作
def on_focus(e):
    #接受editor的焦点事件
    # editor.tk.call(peert, 'configure', '-state', 'normal')
    ...
def out_focus(e):
    #接受editor的焦点事件
    # editor.tk.call(peert, 'configure', '-state', 'disabled')
    ...

def peer_buttonrelease(e):
    #接受peer的焦点事件
    index=editor.tk.call(peert, 'index', 'insert')
    editor.see(index)



def key_call_back(e):
    #接受editor的键入事件
    print(e)
def button_call_back(e):
    #接受editor的鼠标点击事件
    print(e)


def __start():
    #加载窗口
    global root, editor, tintext, peert, already

    already=True
    
    root=Toplevel()
    root.title('TinWriter')
    root.geometry('1200x750+350+100')
    root.resizable(False, False)
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    center_x = int(screen_width / 2 - 1100 / 2)
    # center_y = int(screen_height / 2 - 750 / 2)
    root.geometry('1100x750+%d+%d' % (center_x, 5))
    root.update()

    tinui=BasicTinUI(root,bg='#ffffff')
    tinui.place(x=0, y=0, width=750, height=40)
    tinuix=TinUIXml(tinui)
    tinuix.datas['appbar']=(('','\uE74E',save_file),('','\uE8A1',reopenfunc),('','\uE792',saveas_file),
    '',('','\uE7A7',editor_undo),('','\uE7A6',editor_redo))
    tinuix.loadxml(open('pages/writer.xml',encoding='utf-8').read())
    editor_buttons=tinuix.tags['buttons']

    editor=Text(root, borderwidth=0, relief='flat', font='Consolas 13',
        insertbackground='#000000', insertborderwidth=1, wrap='char',
        undo=True)
    editor.place(x=0, y=40, width=750, height=710)
    # editor.bind('<<Undo>>', editor_undo) #避免重复操作
    # editor.bind('<<Redo>>', editor_redo)
    editor.bind('<MouseWheel>', peer_synchronize)
    # editor.bind('<FocusIn>', on_focus)
    # editor.bind('<FocusOut>', out_focus)
    # editor.bind('<KeyRelease>',on_text_change)
    # editor.bind('<ButtonRelease-1>',button_call_back)
    editor.bind('<<Modified>>', on_text_change)

    editor.tag_config('sel',foreground='',background='#add6ff')
    editor.tag_config('comment',foreground=color_dict['comment'][0],background=color_dict['comment'][1])
    editor.tag_config('separate',foreground=color_dict['separate'][0],background=color_dict['separate'][1])
    editor.tag_config('tag',foreground=color_dict['tag'][0],background=color_dict['tag'][1])
    editor.tag_config('tag_name',foreground=color_dict['tag_name'][0],background=color_dict['tag_name'][1])

    peert='.!toplevel3.!peert'
    # peert='.!toplevel.!peert'
    editor.peer_create(peert,borderwidth=0,relief='flat',font='Consolas 2',
        insertbackground='#000000', insertborderwidth=1, wrap='char',
        cursor='arrow')
    editor.tk.call('place', peert, '-x', 750, '-y', 0 ,'-width', 50, '-height', 400)
    # editor.tk.call('bind', peert, '<MouseWheel>', editor_synchronize)
    utils.bind(editor,peert,'<MouseWheel>',editor_synchronize)
    utils.bind(editor,peert,'<ButtonRelease-1>',peer_buttonrelease)

    toolsui=BasicTinUI(root,bg='#ffffff')
    toolsui.place(x=800, y=0, width=300, height=450)
    toolsui.add_title((5,5),'Comming soon...')

    tintext=TinText(root,font='Consolas 13')
    tintext.place(x=750, y=400, width=350, height=350)
    tintext.config(state='disabled')

    root.protocol('WM_DELETE_WINDOW', closs_writer)
    root.bind('<Control-s>', save_file)
    root.bind('<Control-r>',reopenfunc)

    load_tinfile()
    title_filename=os.path.basename(filename)
    root.title('TinWriter - '+title_filename)

    root.focus_set()