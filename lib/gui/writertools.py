"""
/lib/gui/writertools.py
TinWriter工具
"""
from lib.gui import maker


def initial(_notebook,_editor,_filename):
    #初始化工具页
    global notebook, editor, filename
    notebook = _notebook
    editor = _editor
    filename = _filename

    #short cut page
    scpage=notebook.addpage('快捷键',scrollbar=True,cancancel=False)
    notebook.showpage(scpage)
    scx=notebook.getvdict()[scpage][1]
    # scu=notebook.getvdict()[scpage][0]# 270 x 328
    load_sc(scx)

    #note page
    ntpage=notebook.addpage('笔记',cancancel=False)
    ntx=notebook.getvdict()[ntpage][1]
    # ntu=notebook.getvdict()[ntpage][0]# 287 x 345
    load_nt(ntx)

    #tin generate page
    tgpage=notebook.addpage('生成',cancancel=False)
    tgx=notebook.getvdict()[tgpage][1]
    # tgu=notebook.getvdict()[tgpage][0]# 287 x 345
    load_tg(tgx)

def chagefile(_filename):
    global filename
    filename = _filename


#快捷键
def load_sc(scx):
    xml='''<!--TinUIXml编辑-->
<tinui>
<line>
    <paragraph text='全选&#x0009;ctrl+a'></paragraph>
</line>
<line>
    <paragraph text='复制&#x0009;ctrl+c'></paragraph>
</line>
<line>
    <paragraph text='剪切&#x0009;ctrl+x'></paragraph>
</line>
<line>
    <paragraph text='粘贴&#x0009;ctrl+v'></paragraph>
</line>
<line>
    <paragraph text='撤销&#x0009;ctrl+z'></paragraph>
</line>
<line>
    <paragraph text='重做&#x0009;ctrl+y'></paragraph>
</line>
<line>
    <paragraph text='查找&#x0009;ctrl+f'></paragraph>
</line>
<line>
    <paragraph text='替换&#x0009;ctrl+h'></paragraph>
</line>
<line>
    <paragraph text='重新渲染&#x0009;ctrl+r'></paragraph>
</line>
<line>
    <paragraph text='保存&#x0009;ctrl+s'></paragraph>
</line>
<line>
    <paragraph text='另存为&#x0009;ctrl+shift+s'></paragraph>
</line>
<line x='3'>
    <separate width='260'></separate>
</line>
<line>
    <paragraph text='接受建议&#x0009;alt+p'></paragraph>
</line>
<line>
    <paragraph text='生成参数&#x0009;alt+g'></paragraph>
</line>
<line>
    <paragraph text='加 ;&#x0009;alt+;'></paragraph>
</line>
<line>
    <paragraph text='注释&#x0009;alt+/'></paragraph>
</line>
</tinui>'''
    scx.loadxml(xml)


#记事本
def load_nt(ntx):
    xml='''<!--TinUIXml编辑-->
<tinui>
<line>
<textbox width='265' height='340' scrollbar='True'></textbox>
</line>
</tinui>'''
    ntx.loadxml(xml)


#生成
def load_tg(tgx):
    xml='''<!--TinUIXml编辑-->
<tinui>
<line>
    <button2 text='打开TinMaker' command='self.funcs["openmaker"]'></button2>
</line>
<line>
    <paragraph text='*支持生成 TINP, TINX'></paragraph>
</line>
<line>
    <link text='TIN格式说明' url='https://tintext.smart-space.com.cn/tinml/fileTIN'></link>
</line>
<line>
    <link text='TINP格式说明' url='https://tintext.smart-space.com.cn/tinml/fileTINP'></link>
</line>
<line>
    <link text='TINX格式说明' url='https://tintext.smart-space.com.cn/tinml/fileTINX'></link>
</line>
</tinui>'''
    tgx.funcs['openmaker'] = open_tinmaker
    tgx.loadxml(xml)

def open_tinmaker(e):
    maker.initial(filename)