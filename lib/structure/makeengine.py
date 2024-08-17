"""
/lib/structure/makeengine.py
TinText的打包、集成引擎
"""
import secrets


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