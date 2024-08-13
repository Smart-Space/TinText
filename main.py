"""
TinText Tin富文本标记语言
基于python-TinUI(tkinter)，重塑于TinReader

Copyright since 2024 Smart-Space <smart-space@qq.com|tsan-zane@outlook.com>
"""
import platform
import tkinter as tk
import sys
from multiprocessing import freeze_support, Process, Lock, Pipe

from TinUI import BasicTinUI, TinUIXml

import gui
import process

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

    root=tk.Tk()
    root.withdraw()
    root.after(1,initial)
    root.mainloop()
