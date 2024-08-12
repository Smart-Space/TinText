"""
process.py
TinText的进程消息管理
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
    p.terminate()
    p.close()

def config(*args):
    conn_parent.send(['config',*args])
    return conn_parent.recv()
