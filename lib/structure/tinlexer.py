"""
/lib/structure/tinlexer.py
基于Pygments的TinML词法分析器
"""
import re
from pygments.lexer import RegexLexer, bygroups
from pygments.token import *


class TinLexer(RegexLexer):
    name = 'tin'
    aliases = ['tin']
    filenames = ['*.tin']
    flags = re.IGNORECASE | re.MULTILINE

    tokens = {
        'root': [
            (r'\s+', Text),
            (r'^\|-.*$', Comment),#注释
            (r'^(<)(.*?)(>)(.*)(;)$', bygroups(Keyword, Name.Tag, Keyword, String, Keyword)),#多行
            (r'^(<)(.*?)(>)(.*?)(\|)', bygroups(Keyword, Name.Tag, Keyword, String, Keyword)),#单行多参数
            (r'(<)(.*?)(>)(.*)$', bygroups(Keyword, Name.Tag, Keyword, String)),#单行单参数
            (r'^(\|)(.*)(\|)$', bygroups(Keyword, String, Keyword)),#结束多行
            (r'^(\|)(.*)$', bygroups(Keyword, String)),#多行/单行多项模式参数
            (r'(.*)(\|)', bygroups(String, Keyword)),#单行参数
            ('(.*)\n', String)#单行结尾
        ],
    }