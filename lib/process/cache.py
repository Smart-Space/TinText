"""
/lib/process/cache.py
TinText缓存管理
"""
from threading import Thread
import os
import time


imgs_cache_cleanday = 60 #缓存清理周期(day)
imgs_cache_clean_sec = imgs_cache_cleanday * 86400 #缓存清理周期(秒)

def initial():
    pass

#==========清理缓存==========
def clean_cache_imgs():
    #遍历 data/imgs 目录下所有文件，包括所有子目录
    #如果文件最后修改时间距今超过60天，则删除该文件
    for root, _, files in os.walk('./data/imgs'):
        for file in files:
            path = os.path.join(root, file)
            #获取文件最后修改时间
            mtime = os.stat(path).st_mtime
            #获取当前时间
            ntime = time.time()
            #计算文件最后修改时间距今的时间差
            diff = ntime - mtime
            if diff > imgs_cache_clean_sec:
                os.remove(path)

def clean_cache_tinfile():
    # 遍历 data/tinfile/user 目录下所有文件，包括所有子目录
    # 如果文件最后修改时间距今超过60天，则删除该文件
    for root, _, files in os.walk('./data/tinfile/user'):
        for file in files:
            path = os.path.join(root, file)
            # 获取文件最后修改时间
            mtime = os.stat(path).st_mtime
            # 获取当前时间
            ntime = time.time()
            # 计算文件最后修改时间距今的时间差
            diff = ntime - mtime
            if diff > imgs_cache_clean_sec:
                os.remove(path)

def clean_cache(filetype):
    if filetype == 'imgs':
        t=Thread(target=clean_cache_imgs)
        t.start()
    elif filetype == 'tinfile':
        t = Thread(target=clean_cache_tinfile)
        t.start()


#====================
def loop(command,*args):
    #处理 cache 命令
    if command == 'clean':
        #清理缓存
        filetype=args[0]#文件类型，目前支持data/imgs/*
        clean_cache(filetype)
        return None