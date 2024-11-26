"""
TinText Tin富文本标记语言实现平台/软件
基于python-TinUI(tkinter)，重塑于TinReader

project-url: https://tintext.smart-space.com.cn
project-dev: https://github.com/smart-space/tintext

Copyright since 2024 Junming Zhang(Smart-Space) <smart-space@qq.com|tsan-zane@outlook.com>
基于GPLv3协议发布，见gpl-3.0.md

其它第三方库开源协议见./data/licenses/*。注意，html2text是不必要的，TinText tin转md 功能可作为拓展使用
"""
import platform
# import ctypes
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

    # if platform.system()=='Windows':
    #     try:
    #         ctypes.windll.shcore.SetProcessDpiAwareness(1)
    #         ScaleFactor=ctypes.windll.shcore.GetScaleFactorForDevice(0)
    #         root.tk.call('tk','scaling',96*ScaleFactor/100/72)
    #         win_handle=ctypes.wintypes.HWND(root.winfo_id())
    #         monitor_handle=ctypes.windll.user32.MonitorFromWindow(win_handle,2)
    #         x_dpi=ctypes.wintypes.UINT()
    #         y_dpi=ctypes.wintypes.UINT()
    #         ctypes.windll.shcore.GetDpiForMonitor(monitor_handle,0,ctypes.pointer(x_dpi),ctypes.pointer(y_dpi))
    #     except Exception:
    #         pass

    html=tkinterweb.HtmlFrame(root,messages_enabled=False)#载入tkhtml框架
    html.pack(expand=True,fill='both')
    root.after(1,initial)
    # root.iconbitmap('./logo.ico')
    root.mainloop()
