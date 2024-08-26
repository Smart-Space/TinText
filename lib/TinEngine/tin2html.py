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
                res.append(br())
            elif text[0]==' ':
                res.append(text[1:])
            elif text[0] not in self.tinPmark:
                res.append(text)
            else:
                head_mark=text[:6]
                head_num=0
                now_p=None#初始化，空
                if '*' in head_mark: head_num+=1
                if '/' in head_mark: head_num+=1
                if '_' in head_mark: head_num+=1
                if '-' in head_mark: head_num+=1
                if '=' in head_mark: head_num+=1
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
                if '=' in head_mark:
                    if now_p:
                        now_p=mark(now_p)
                    else:
                        now_p=mark(text[head_num:])
                res.append(now_p)
        return res

    def tohtml(self,_title='TinText',_style=''):
        #tin->html
        doc=dominate.document(title=_title)
        doc.head.add(meta(charset='utf-8'))
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
            elif tag == '<img>':
                #图片
                url=kw['url']
                size=kw['size']
                if url=='':
                    #目前暂不支持没有网络来源的图片
                    continue
                if size:
                    width,height=size
                    _body.add(img(src=url,alt='',width=width,height=height))
                else:
                    _body.add(img(src=url,alt=''))
            elif tag == '<note>':
                #引用或说明
                notes=kw['note']
                _quote=blockquote()
                for note in notes:
                    _quote.add(p(note))
                _body.add(_quote)
            elif tag == '<tb>':
                #表格
                data=kw['data']
                _table=table()
                _table_head=thead()
                _table_row=tr()
                for head in data[0]:#表头
                    _table_row.add(th(head))
                _table_head.add(_table_row)
                _table.add(_table_head)
                _table_body=tbody()
                for row in data[1:]:#表格数据
                    _table_row=tr()
                    for col in row:
                        _table_row.add(td(col))
                    _table_body.add(_table_row)
                _table.add(_table_body)
                _body.add(_table)
            elif tag == '<ac>':
                #锚点
                name=kw['name']
                if name.startswith('#'):#前往锚点
                    item=_body[-1]
                    item.add(a('🔗',href=name))
                else:#定义锚点
                    _body.add(a(id=name))
        return doc
    
    # def __tinP_to_markdown(self,texts):
    #     #tin段落转markdown
    #     res=[]
    #     for text in texts:
    #         if text=='':
    #             continue
    #         elif text[0]==' ':
    #             res.append(text[1:])
    #             continue
    #         elif text[0] not in self.tinPmark:
    #             res.append(text)
    #             continue
    #         head_num=0
    #         head_mark=text[:5]
    #         if '*' in head_mark: head_num+=1
    #         if '/' in head_mark: head_num+=1
    #         if '_' in head_mark: head_num+=1
    #         if '-' in head_mark: head_num+=1
    #         _text=text[head_num:]
    #         if '!' in head_mark:
    #             result=self.tinPlink_re.match(text)
    #             if result:
    #                 url_text,url=result.groups()
    #                 if url_text=='':
    #                     url_text=url
    #                 _text='[%s](%s)'%(url_text,url)
    #             else:
    #                 _text=text[head_num:]
    #         if '*' in head_mark:
    #             _text=f'**{_text}**'
    #         if '/' in head_mark:
    #             _text=f'*{_text}*'
    #         if '_' in head_mark:
    #             _text=f'<u>{_text}</u>'
    #         if '-' in head_mark:
    #             _text=f'~~{_text}~~'
    #         res.append(_text)
    #     return ' '.join(res)
    
    # def tomarkdown(self):#nothing
    #     #显然，那些html转markdown的库，有一些规范性的问题，这也是markdown渲染平台的通病，缺乏绝对统一
    #     #tin->markdown
    #     res=''
    #     for tag,kw in self.tinml:
    #         if tag == '<title>':
    #             text=kw['title']
    #             level=int(kw['level'])
    #             if level==1:
    #                 res+='# '+text+'\n\n'
    #             elif level==2:
    #                 res+='## '+text+'\n\n'
    #             elif level==3:
    #                 res+='### '+text+'\n\n'
    #             elif level==4:
    #                 res+='#### '+text+'\n\n'
    #             elif level==5:
    #                 res+='##### '+text+'\n\n'
    #             elif level==6:
    #                 res+='###### '+text+'\n\n'
    #         elif tag == '<p>':
    #             texts=kw['text']
    #             mdtexts=self.__tinP_to_markdown(texts)
    #             res+=mdtexts+'\n\n'
    #         elif tag == '<lnk>':
    #             text=kw['text']
    #             url=kw['url']
    #             res+='[%s](%s)\n\n'%(text,url)
    #         elif tag == '<sp>':
    #             res+='---\n\n'
    #         elif tag == '<note>':
    #             notes=kw['note']
    #             for note in notes:
    #                 res+='> '+note+'\n'
    #             res+='\n'
    #         elif tag == '<img>':
    #             name=kw['filename']
    #             url=kw['url']
    #             res+='![%s](%s)'%(name,url)
    #         elif tag == '<tb>':
    #             data=kw['data']
    #             res+='|'+'|'.join(data[0])+'|\n'
    #             length=len(data[0])
    #             res+='|'+'|'.join(['---']*length)+'|\n'
    #             for row in data[1:]:
    #                 res+='|'+'|'.join(row)+'|\n'
    #             res+='\n'
    #     return res
