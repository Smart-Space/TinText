"""
/lib/structure/__init__.py
TinText的自定义类，用以区分不同类型的数据载体（轻型）
"""
import configparser


class Functions():
    #用于捆绑多个方法、函数

    start=None

    def __init__(self):
        pass


class SettingDict():
    #TinText设置类，ini格式

    def __init__(self,filename=''):
        #filename是相对于./data/settings的
        #比如 filename='general.ini'
        self.filename='./data/settings/'+filename
        self.cfg=configparser.ConfigParser()
        self.cfg.read(self.filename,encoding='utf-8')

    def get(self,item,key):
        return self.cfg[item][key]
    
    def get_item(self,item):
        return self.cfg[item]

    def set(self,item,key,val):
        self.cfg[item][key]=val

    def add(self,item,key,val):
        #不判断是否已经存在key
        self.cfg[item][key]=val
    
    def add_item(self,item):
        if item not in self.cfg:
            self.cfg[item]={}
    
    def save(self):
        self.cfg.write(open(self.filename,'w',encoding='utf-8'))
