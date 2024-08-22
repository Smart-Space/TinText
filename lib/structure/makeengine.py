"""
/lib/structure/makeengine.py
TinText的打包、集成引擎
"""
import secrets
from zipfile import ZipFile
import os
import re


headnums=range(125,256)


#*.tinp make engine
class TinpMakeEngine:
    """
    tin -> tinp Tin普通加密格式
    [in] text, key
    1. 在文本第一行添加随机125~255字符
    2. 用key加密文本 (XOR)
    [out] text
    [exception out] None ( len(key)>len(text) )
    """

    def __init__(self,text):
        self.text=text

    def encrypt(self, key:str):
        #加密
        head_num=secrets.choice(headnums)
        head=secrets.token_hex(head_num)+'\n'

        text=list(head+self.text)
        key=list(key)
        
        if len(key)<len(text):
            key += key * (len(text) // len(key))
            key += key[:len(text) % len(key)]
        elif len(key)>len(text):#密码不能长于文本
            return None
        
        encrypted_text = ''.join(chr(ord(text_char) ^ ord(key_char)) for text_char, key_char in zip(text, key))
        return encrypted_text

    def decrypt(self, key:str):
        #解密
        text=list(self.text)
        key=list(key)
        
        if len(key)<len(text):
            key += key * (len(text) // len(key))
            key += key[:len(text) % len(key)]
        elif len(key)>len(text):#密码不能长于文本
            return None
            
        encrypted_text = ''.join(chr(ord(text_char) ^ ord(key_char)) for text_char, key_char in zip(text, key))
        result='\n'.join(encrypted_text.split('\n')[1:])
        return result


#*.tinx make engine
class TinxMakeEngine:
    """
    tin -> tinx Tin集成格式
    TINX-include-file:
    {tinfile}.tin -> {tinfile}.tinp
    data/imgs/* -> imgs/* [needed from <img>]
    ...

    [in] tinfile, key
    [all] -> {tinfile}.zip (encrypted)
    """

    def __init__(self,tinfile,log):
        self.tinfile=tinfile
        self.log=log
        self.img_re=re.compile('^[ ]{0,}(<img>|<image>)(.*)$',re.M)
    
    def encrypt(self, key:str):
        #加密
        #ZIP初始化，获取tinfile的文件目录和文件名(无后缀)，改为*.tinx
        path=os.path.dirname(self.tinfile)
        name=os.path.basename(self.tinfile).split('.')[0]
        tinxfile=os.path.join(path, name+'.tinx')
        zipf=ZipFile(tinxfile, 'w')
        #主文件部分 TIN -> TINP
        with open(self.tinfile, 'r', encoding='utf-8') as f:
            text=f.read()+'\n'
        tinp=TinpMakeEngine(text)
        tinp_text=tinp.encrypt(key)
        tinp_text_b=tinp_text.encode('utf-8','surrogatepass')
        zipf.writestr('main.tinp', tinp_text_b)
        self.log('TINP文件已生成')
        #data/imgs* -> imgs/*
        self.log('开始处理图片……')
        imgpath='./data/imgs/'
        img_tags=self.img_re.findall(text)
        for tag in img_tags:
            imgname=tag[1].split('|')[0]
            if imgname=='':#文件名为空
                continue
            imgfile=imgpath+imgname
            if not os.path.exists(imgfile):
                #若不存在图片文件，只是提醒，不会报错
                self.log('图片不存在：'+imgname)
            else:
                zipf.write(imgfile, 'imgs/'+imgname)
        self.log('图片已打包')
        #... other file types (future)
        #all -> zip
        zipf.close()
        return None
    
    def decrypt(self, key:str):
        #解密
        #初始化zipfile
        zipf=ZipFile(self.tinfile, 'r')
        #tinp -> tin
        tinptext=zipf.read('main.tinp').decode('utf-8','surrogatepass')
        tinp=TinpMakeEngine(tinptext)
        text=tinp.decrypt(key)
        #imgs/* -> data/imgs*
        imgpath='./data/imgs/'
        for file in zipf.namelist():
            if file.startswith('imgs/'):
                img_name=file[5:]
                img_data=zipf.read(file)
                with open(imgpath+img_name, 'wb') as f:
                    f.write(img_data)
        #... other file types (future)
        return text
