"""
/lib/gui/writer.py
具有*.tin&*.tinx编辑功能的窗口，即TinWriter

设计上作为TinReader的下一级，通过TinReader调用
"""
from tkinter import Toplevel
from tkinter.font import Font
from tkinter.filedialog import asksaveasfilename
import os
from concurrent.futures import ThreadPoolExecutor

from tinui import BasicTinUI, TinUIXml, show_info, show_warning, show_question, show_success, show_error

import lib.gui.utils as utils
import lib.gui.writertools as writertools
from lib.TinEngine import TinText
import process


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
        writerhelper.start()
        writertools.chagefile(filename)
    else:
        __start()

def close_writer():
    #关闭窗口，并保存文件
    #若文件为保存，询问是否保存
    global SAVE
    if SAVE:
        pass
    else:
        if show_question(root,'该文件未保存','是否在编辑器关闭之前保存该文件？'):
            save_file(None)
    SAVE=True
    writerhelper.ON=False
    root.withdraw()
    readerroot.focus_set()


def load_tinfile():
    #加载文件，并显示在窗口中
    editor.delete('1.0', 'end')
    with open(filename, 'r', encoding='utf-8') as f:
        editor.insert('end', f.read())
    editor.edit_modified(False)
    title_filename=os.path.basename(filename)
    root.title('TinWriter - '+title_filename)
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
    newname=asksaveasfilename(title='另存为tin文件',filetypes=[('Tin文件','*.tin')])
    if not newname:
        return
    if not newname.endswith('.tin'):
        newname+='.tin'
    if newname:
        with open(newname,'w',encoding='utf-8') as f:
            f.write(editor.get('1.0','end-1c'))


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


#切换注释
def toggle_comment(e):
    try:
        sel_start=editor.index('sel.first')
        sel_end=editor.index('sel.last')
    except:
        sel_start=editor.index('insert')
        sel_end=editor.index('insert')
    startline=int(__get_index_line(sel_start))
    endline=int(__get_index_line(sel_end))
    startchar=editor.get(f'{startline}.0',f'{startline}.0 +2c')
    if startchar!='|-':
        for i in range(startline,endline+1):
            editor.insert(f'{i}.0', f'|-')
    else:
        for i in range(startline,endline+1):
            char=editor.get(f'{i}.0', f'{i}.0 +2c')
            if char=='|-':#如果当前字符是|-，则删除
                editor.delete(f'{i}.0', f'{i}.0 +2c')

# 添加标签<>
def add_tag_sign(e):
    index = editor.index('insert')
    if index.split('.')[1] == '0':
        editor.insert('insert', '<>')
        editor.mark_set('insert', f'{index}+1c')
    else:
        pass


def open_textfinder(e):
    #打开文本查找器
    textfinder.show()
def open_textfinder_replace(e):
    #打开文本替换器
    textfinder.show(replace=True)
def open_htmlinputer(e):
    #打开html输入器
    writerhtmlinputer.show()
def open_tabinputer(e):
    #打开表格输入器
    tabinputer.show()
def open_codeinputer(e):
    #打开代码输入器
    codeinputer.show()
def open_resourcemanager(e):
    # 打开资源管理器
    # include:
    # - ./data/imgs/
    # - ./data/tinfile/user/
    resourcemanager.show()


def on_text_change(e):
    # Handle the text change event from the editor.
    global SAVE, highlighttask
    if not editor.edit_modified():
        return
    editor.edit_modified(0)
    if SAVE:
        SAVE = False
        title_filename = os.path.basename(filename)
        root.title(f'TinWriter - *{title_filename}')
    if highlighttask.done():
        highlighttask = highlightthreads.submit(highlight)

def __get_index_line(index):
    #返回index所在行号
    return index.split('.')[0]
def __get_index_char(index):
    #返回index所在列号
    return index.split('.')[1]
def highlight(all=False,startpos='insert-30l linestart',endpos='insert+30l lineend'):
    #代码高亮
    if all:#全部高亮
        s='1.0'
        end='end'
    else:#部分高亮
        s=editor.index(startpos)
        end=editor.index(endpos)
    #以下循环匹配，用s代指start
    #分隔符
    linemode=False#多行模式
    tagflag=False#标签模式
    tagstart=None#标签起始位置
    tagend=None#标签结束位置
    while True:
        pos=editor.search('(;|\||-|<|>)', s, end, regexp=True)
        if not pos:
            break
        if __get_index_char(pos) == '0' and editor.get(pos, f"{pos}+2c") != '|-':
            # 当位置为开头且不是|-时，才删除样式
            for tag in color_tags:
                editor.tag_remove(tag, pos, f"{pos} lineend")
        char=editor.get(pos)
        if char==';':
            line_context=editor.get(f"{pos} linestart", f"{pos} lineend")
            if line_context.lstrip()[0] not in ('<','|'):
                #开头不是标签，则跳过
                s=f"{pos} +1l linestart"
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
            if editor.get(f'{pos}+1c')=='-':
                #注释
                if __get_index_char(pos)=='0':#开头
                    comment_s=f"{pos} linestart"
                    comment_e=f"{pos} lineend"
                    editor.tag_add('comment', comment_s, comment_e)
                    s=f"{pos}+1l linestart"
                    continue
                else:
                    pass
            line_context=editor.get(f"{pos} linestart", f"{pos} lineend")
            if linemode:#开启了多行模式
                #判断是不是在行末终止了多行模式
                line_last=f"{pos} lineend -1c"
                if __get_index_char(pos)=='0':#开头
                    editor.tag_add('separate', pos)
                    if line_context.lstrip()=='|':
                        s=f"{pos}+1l linestart"
                    else:
                        s=f"{pos} lineend-1c"
                elif pos==editor.index(line_last):#结尾
                    linemode=False
                    editor.tag_add('separate', pos)
                    s=f"{pos}+2c"
                else:
                    #防止没有结尾匹配出错
                    s=f"{pos}+1c"
            elif line_context.lstrip()[0]!='<':
                #开头不是标签，则跳过
                s=f"{pos}+1l linestart"
            else:
                #判断行末是不是;开启了多行模式
                line_last=f"{pos} lineend -1c"
                if editor.get(line_last)==';':
                    s=f"{pos} lineend -1c"
                else:
                    #若是单行模式，则正常高亮
                    editor.tag_add('separate', pos)
                    s=f"{pos}+1c"
        elif char=='<':
            if __get_index_char(pos)!='0':
                s=f"{pos}+1c"
                continue
            tagflag=True
            tagstart=pos
            s=f"{pos}+1c"
        elif char=='>':
            if not tagflag:
                s=f"{pos}+1c"
                continue
            tagflag=False
            tagend=pos
            editor.tag_add('tag', tagstart)
            editor.tag_add('tag', tagend)
            editor.tag_add('tag_name', f"{tagstart}+1c", tagend)
            s=f"{pos}+1c"
            tagstart=None
            tagend=None
        else:
            s=f"{pos}+1c"
    #处理标签
    editor.tag_raise('tag')
    editor.tag_raise('tag_name')
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
    global root, editor, tintext, peert, already,\
         textfinder, writerhelper, writerhtmlinputer,\
         tabinputer, codeinputer, resourcemanager,\
         highlighttask, highlightthreads

    already=True
    
    root=Toplevel()
    root.withdraw()
    root.title('TinWriter')
    root.iconbitmap('./logo.ico')
    root.geometry('1200x750+350+100')
    root.resizable(False, False)
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    center_x = int(screen_width / 2 - 1100 / 2)
    root.geometry('1100x750+%d+%d' % (center_x, 5))
    root.update()

    tinui=BasicTinUI(root,bg='#ffffff')
    tinui.place(x=0, y=0, width=750, height=40)
    tinuix=TinUIXml(tinui)
    tinuix.datas['appbar']=(
        ('','\uE74E',save_file),('渲染','\uE8A1',reopenfunc),('另存为','\uE792',saveas_file),
        '',('搜索','\uE721',open_textfinder),('替换','\uE8EE',open_textfinder_replace),
        '',('HTML','\uF57E',open_htmlinputer),('表格','\uF0E2',open_tabinputer),('代码','\uE943',open_codeinputer),('文件资源','\uECCD',open_resourcemanager),
        '',('','\uE7A7',editor_undo),('','\uE7A6',editor_redo),
    )
    tinuix.loadxml(open('pages/writer.xml',encoding='utf-8').read())
    tinuix.tags['buttons']# editor_buttons

    editor=utils.ScrolledText(root, borderwidth=0, relief='flat', font='Consolas 13',
        insertbackground='#000000', insertborderwidth=1, wrap='char', spacing1=2,spacing3=2,
        undo=True)
    editor.place(x=0, y=40, width=750, height=690)
    editor_font = Font(font=editor['font'])
    editor.config(tabs=editor_font.measure('    '))# 四个空格
    # editor.bind('<<Undo>>', editor_undo) #避免重复操作
    # editor.bind('<<Redo>>', editor_redo)
    editor.bind('<MouseWheel>', peer_synchronize)
    editor.bind('<Alt-;>',lambda e: editor.insert('insert',';'))
    editor.bind('<Alt-/>',toggle_comment)
    editor.bind('<Alt-.>', add_tag_sign)
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

    peert=root._w+'.!peert'
    # peert='.!toplevel.!peert'
    editor.peer_create(peert,borderwidth=0,relief='flat',font='Consolas 2',
        insertbackground='#000000', insertborderwidth=1, wrap='char',
        cursor='arrow')
    editor.tk.call('place', peert, '-x', 750, '-y', 0 ,'-width', 50, '-height', 400)
    # editor.tk.call('bind', peert, '<MouseWheel>', editor_synchronize)
    utils.bind(editor,peert,'<MouseWheel>',editor_synchronize)
    utils.bind(editor,peert,'<ButtonRelease-1>',peer_buttonrelease)

    lineviewer=utils.LineViewer(root,editor)
    lineviewer.place(x=0, y=730, width=750, height=20)

    toolsui=BasicTinUI(root,bg='#ffffff')
    toolsui.place(x=800, y=0, width=300, height=400)
    toolsuix=TinUIXml(toolsui)
    toolsuix.loadxml(open('./pages/writer-tools.xml',encoding='utf-8').read())
    toolsbook=toolsuix.tags['ntbook'][-2]#notebook funcs
    writertools.initial(toolsbook,editor,filename)

    tintext=TinText(root,font='微软雅黑 12')
    tintext.place(x=750, y=400, width=350, height=350)
    tintext.config(state='disabled')

    root.protocol('WM_DELETE_WINDOW', close_writer)
    root.bind('<Control-s>', save_file)
    root.bind('<Control-Shift-S>', saveas_file)
    root.bind('<Control-r>',reopenfunc)
    root.bind('<Control-f>',open_textfinder)
    root.bind('<Control-h>',open_textfinder_replace)

    root.deiconify()

    load_tinfile()
    title_filename=os.path.basename(filename)
    root.title('TinWriter - '+title_filename)

    writerhelper=utils.WriterHelper(editor,tintext)

    #获取配置信息
    searchmode=process.config('get_item','general','WriterSearchMode')

    textfinder = utils.TextFinder('TinWriter搜索',editor,searchmode,'WriterSearchMode')
    writerhtmlinputer = utils.WriterHtmlInputer(editor)
    tabinputer = utils.WriterTabInputer(editor)
    codeinputer = utils.WriterCodeInputer(editor)
    resourcemanager = utils.WriterResourceManager(editor)

    root.focus_set()
    highlightthreads = ThreadPoolExecutor(2)
    highlighttask = highlightthreads.submit(highlight)

