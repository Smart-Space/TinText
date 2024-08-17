"""
/lib/process/configfile.py
TinText的后端进程-配置文件
"""
import os

from lib.structure import SettingDict

config_files=(
    'general', # settings/general.ini
)

def initial():
    global config_parsers
    config_parsers=dict()
    for i in config_files:
        config_parsers[i]=SettingDict(f'{i}.ini')

def loop(command,*args):
    #处理 config 命令
    if command=='get':
        #get filename itemname key
        return config_parsers[args[0]].get(args[1], args[2])
    elif command=='get_item':
        #get filename itemname
        return config_parsers[args[0]].get_item(args[1])
    elif command=='set':
        #set filename itemname key value
        config_parsers[args[0]].set(args[1], args[2], args[3])
    elif command=='add':
        #add filename itemname key value
        config_parsers[args[0]].add(args[1], args[2], args[3])
    elif command=='add_item':
        #add filename itemname
        config_parsers[args[0]].add_item(args[1])
    elif command=='save':
        #save filename
        config_parsers[args[0]].save()