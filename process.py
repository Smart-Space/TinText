"""
process.py
TinText的进程消息管理
操作流在这里堵塞，但是不阻塞主进程
"""
from multiprocessing import Process, Lock, Queue, Pipe, Pool
from threading import Thread

from lib.process.multi import initial_process


def initial():
    global conn_parent, p
    conn_parent, conn_child = Pipe()
    p = Process(target=initial_process, args=(conn_child,))
    p.start()

def close():
    try:
        p.terminate()#终止进程
        p.close()#关闭进程
    except:
        pass


def config(*args):
    conn_parent.send(['config',*args])
    return conn_parent.recv()

def version(*args):
    conn_parent.send(['version',*args])
    return conn_parent.recv()

def cache(*args):
    conn_parent.send(['cache',*args])
    return conn_parent.recv()
