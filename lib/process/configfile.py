"""
/lib/process/configfile.py
TinText的后端进程-配置文件
"""
import os

from lib.structure import SettingDict

config_files=(
    'general', # settings/general.ini
    'output', # settings/output.ini
    'theme', # settings/theme.ini
)

ver = '1.6'

origin_general = f'''[Version]
ver = {ver}

[ReaderSearchMode]
loop = True
regexp = False
case = True
webengine = 

[WriterSearchMode]
loop = True
regexp = False
case = True
replace_all = True
'''

origin_output = '''[html]
css = ./data/render/blubook.css
'''

origin_theme = '''; not used, just for testing
[Reader]
theme = light

[Writer]
theme = light

[Maker]
theme = light
'''

def initial():
    global config_parsers
    # 判断./data/settings目录是否存在，不存在则创建
    if not os.path.exists('./data/settings'):
        os.makedirs('./data/settings')
        # 创建配置文件
        with open('./data/settings/general.ini', 'w', encoding='utf-8') as f:
            f.write(origin_general)
        with open('./data/settings/output.ini', 'w', encoding='utf-8') as f:
            f.write(origin_output)
        with open('./data/settings/theme.ini', 'w', encoding='utf-8') as f:
            f.write(origin_theme)
    config_parsers=dict()
    for i in config_files:
        config_parsers[i]=SettingDict(f'{i}.ini')
    if config_parsers['general'].get('Version','ver') != ver:
        # 版本不同，更新配置文件
        config_parsers['general'].set('Version','ver', ver)
        config_parsers['general'].save()

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