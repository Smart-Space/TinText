"""
/lib/process/multi.py
TinText的后端进程管理模块

通讯模式采用管道-命令列表通讯
[cmd-name, cmd-args]
"""
from multiprocessing import Process, Lock, Queue, Pool, Pipe


def initial_process(conn_child):
    from .configfile import initial as config_initial, loop as config_loop
    from .version import initial as version_initial, loop as version_loop

    config_initial()
    version_initial()

    while True:
        cmd=conn_child.recv()
        if cmd[0]=='config':
            conn_child.send(config_loop(*cmd[1:]))
        elif cmd[0]=='version':
            conn_child.send(version_loop(*cmd[1:]))