"""
TinText Tin富文本标记语言
基于python-TinUI(tkinter)，重塑于TinReader

project-url: https://tintext.smart-space.com.cn
project-dev: https://github.com/smart-space/tintext

Copyright since 2024 Junming Zhang(Smart-Space) <smart-space@qq.com|tsan-zane@outlook.com>
"""
import platform
import tkinter as tk
import sys
import os
(os.path.dirname(os.path.realpath(__file__)))
from multiprocessing import freeze_support, Process, Lock, Pipe

import tkinterweb
from tinui import BasicTinUI, TinUIXml

import gui
import process

#获取程序所在目录，设置该目录为工作目录
rootpath=sys.path[0]
os.chdir(rootpath)


def quit():
    #允许子窗口调用，完全退出
    process.close()#关闭后端进程
    sys.exit()

if __name__=='__main__':
    process.initial()

    def initial():
        if len(sys.argv)>1:#已有文件被指定加载
            gui.start_reader_with_file(sys.argv[1],quit)
        else:#常规启动
            gui.start_reader(quit)
            
        #启动后操作
        process.cache('clean','imgs')#清理图片缓存

    root=tk.Tk()
    root.withdraw()
    html=tkinterweb.HtmlFrame(root,messages_enabled=False)#载入tkhtml框架
    html.pack(expand=True,fill='both')
    root.after(1,initial)
    # root.iconbitmap('./logo.ico')
    root.mainloop()
