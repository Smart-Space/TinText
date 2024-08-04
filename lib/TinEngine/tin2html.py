"""
tin->html工具类
"""
import re

import dominate
from dominate.tags import *

class TinML(list):
    """
    tin->html的中间工具
    本质上是一个大型列表，可嵌套
    addtin(tag, **kw) - 加载tin解析内容
    clear() - 清空
    """

    def __init__(self):
        super().__init__()

    def addtin(self,tag,**kw):
        super().append((tag,kw))

    def clear(self):
        super().clear()


class TinTranslator():
    """
    tin->html的转译工具类
    *后续可能支持tin->markdown
    """

    def __init__(self,tinml:TinML):
        self.tinml=tinml
        self.doc=None
        
        self.tinPmark=('*','/','_','-','!')
        self.tinPlink_re=re.compile('.*?!\[(.*?)\]\((..*?)\)')
    
    def __tinP_to_html(self,texts):
        #tin段落转html段落
        res=[]
        for text in texts:
            if text=='':
                continue
            elif text[0]==' ':
                res.append(text[1:])
            elif text[0] not in self.tinPmark:
                res.append(text)
            else:
                head_mark=text[:5]
                head_num=0
                now_p=None#初始化，空
                if '*' in head_mark: head_num+=1
                if '/' in head_mark: head_num+=1
                if '_' in head_mark: head_num+=1
                if '-' in head_mark: head_num+=1
                #开始具体转义html<p>
                if '!' in head_mark:
                    result=self.tinPlink_re.match(text)
                    if result:
                        url_text,url=result.groups()
                        if url_text=='':
                            url_text=url
                        now_p=a(url_text,href=url)
                    else:
                        head_num+=1
                if '*' in head_mark:
                    if now_p:
                        now_p=b(now_p)
                    else:
                        now_p=b(text[head_num:])
                if '/' in head_mark:
                    if now_p:
                        now_p=i(now_p)
                    else:
                        now_p=i(text[head_num:])
                if '_' in head_mark:
                    if now_p:
                        now_p=u(now_p)
                    else:
                        now_p=u(text[head_num:])
                if '-' in head_mark:
                    if now_p:
                        now_p=s(now_p)
                    else:
                        now_p=s(text[head_num:])
                res.append(now_p)
        return res

    def tohtml(self,_title='TinText',_style=''):
        #tin->html
        doc=dominate.document(title=_title)
        if _style!='':
            doc.head.add(style(_style))
        _body=div()
        doc.body.add(_body)
        for tag,kw in self.tinml:
            if tag == '<title>':
                #标题
                text=kw['title']
                level=int(kw['level'])
                if level==1:
                    _body.add(h1(text))
                elif level==2:
                    _body.add(h2(text))
                elif level==3:
                    _body.add(h3(text))
                elif level==4:
                    _body.add(h4(text))
                elif level==5:
                    _body.add(h5(text))
                elif level==6:
                    _body.add(h6(text))
            elif tag == '<p>':
                #段落
                texts=kw['text']
                _p=p('')
                htmltexts=self.__tinP_to_html(texts)
                for htmltext in htmltexts:
                    _p.add(htmltext)
                _body.add(_p)
            elif tag == '<lnk>':
                #链接
                text=kw['text']
                url=kw['url']
                _body.add(p(a(text,href=url)))
            elif tag == '<sp>':
                #分割线
                _body.add(hr())
        return doc
