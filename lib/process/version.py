"""
/lib/process/version.py
TinText的后端进程-版本信息
"""
import webbrowser

import requests


def initial():
    global general_ini_parser
    from .configfile import config_parsers
    general_ini_parser = config_parsers['general']

def loop(command,*args):
    #处理 version 命令
    if command == 'this':
        #this
        return general_ini_parser.get('Version','ver')
    if command == 'check':
        #check
        #从 https://tintext.smart-space.com.cn/ver.txt 获取最新版本号
        res=requests.get('https://tintext.smart-space.com.cn/ver.txt')
        version=res.text
        return version
    if command == 'update':
        #update
        webbrowser.open('https://github.com/Smart-Space/TinText/releases')
        return None