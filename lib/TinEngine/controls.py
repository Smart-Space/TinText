"""
TinText内部控件
"""
import tkinter as tk
from tkinter import ttk
from PIL import Image,ImageTk
from tinui import BasicTinUI, TinUI, TinUIXml


class ScrolledText(tk.Text):
    """
    使用ttk重写支持滚动条的文本框
    """
    def __init__(self, master=None, **kw):
        self.frame=tk.Frame(master)

        self.vbar=ttk.Scrollbar(self.frame)
        self.vbar.pack(side='right',fill='y')

        kw.update({'yscrollcommand':self.vbar.set})
        tk.Text.__init__(self,self.frame,**kw)
        self.pack(side='left',fill='both',expand=True)
        self.vbar['command']=self.yview

        text_meths=vars(tk.Text).keys()
        methods=vars(tk.Pack).keys() | vars(tk.Grid).keys() | vars(tk.Place).keys()
        methods=methods.difference(text_meths)

        for m in methods:
            if m[0]!='_' and m!='config' and m!='configure':
                setattr(self,m,getattr(self.frame,m))
    
    def __str__(self):
        return str(self.frame)


class Balloon:
    #基于TinUI tooltip的气泡提示框
    #将其移植到普通tkinter控件可用，参数与TinUI相同

    def __init__(self,text='balloon text',fg='#3b3b3b',bg='#e7e7e7',outline='#3b3b3b',font='微软雅黑 12',tran='#01FF11'):
        toti=tk.Toplevel()
        toti.overrideredirect(True)
        toti.withdraw()
        bar=BasicTinUI(toti,bg=tran)
        bar.pack(fill='both',expand=True)
        self.info=bar.create_text((10,10),text=text,fill=fg,font=font,anchor='nw')
        bbox=list(bar.bbox(self.info))
        tlinemap=((bbox[0]-1,bbox[1]-1),(bbox[2]+1,bbox[1]-1),(bbox[2]+1,bbox[3]+1),(bbox[0]-1,bbox[3]+1))
        self.tline=bar.create_polygon(tlinemap,fill=outline,outline=outline,width=15)
        start=bbox[2]-bbox[0]
        gomap=((bbox[0],bbox[1]),(bbox[2],bbox[1]),(bbox[2],bbox[3]),(bbox[0],bbox[3]))
        self.tback=bar.create_polygon(gomap,fill=bg,outline=bg,width=15)
        bar.tkraise(self.info)
        #屏幕尺寸
        self.maxx=toti.winfo_screenwidth()
        self.maxy=toti.winfo_screenheight()
        toti.attributes('-transparent',tran)
        toti.attributes('-alpha',0.9)#透明度90%
        self.toti=toti
        self.bar=bar
        self.fg=fg
        self.bg=bg
        self.outline=outline

    def show(self,event,text='balloon text'):
        self.bar.itemconfig(self.info,text=text)
        bbox=list(self.bar.bbox(self.info))
        self.width=bbox[2]-bbox[0]+10
        self.height=bbox[3]-bbox[1]+10
        bbox[0]+=5
        bbox[1]+=5
        bbox[2]-=5
        bbox[3]-=5
        #绘制圆角边框
        tlinemap=(bbox[0]-1,bbox[1]-1,bbox[2]+1,bbox[1]-1,bbox[2]+1,bbox[3]+1,bbox[0]-1,bbox[3]+1)
        self.bar.coords(self.tline,*tlinemap)
        start=bbox[2]-bbox[0]
        gomap=(bbox[0],bbox[1],bbox[2],bbox[1],bbox[2],bbox[3],bbox[0],bbox[3])
        self.bar.coords(self.tback,*gomap)
        sx,sy=event.x_root,event.y_root
        if sx+self.width>self.maxx:
            x=sx-self.width
        else:
            x=sx
        if sy+self.height>self.maxy:
            y=sy-self.height
        else:
            y=sy
        self.toti.geometry(f'{self.width+20}x{self.height+20}+{x}+{y}')
        self.toti.update()
        self.toti.deiconify()

    def hide(self,event):
        self.toti.withdraw()


class TinTextSeparate(tk.Canvas):
    #TinText内部控件，用作分割线
    def __init__(self,tintext,width,color):
        super().__init__(master=tintext,width=width,bg=color,relief='flat',
        highlightthickness=0,height=2)


class TinTextNote(tk.Canvas):
    #TinText的引用说明框
    def __init__(self,tintext,width,notes,font,markcolor,fg,bg,markbg):
        """
        notes:list
        markcolor:str
        fg:str
        bg:str 画布颜色
        markbg:str 文本背景色
        """
        super().__init__(master=tintext,width=width,bg=bg,relief='flat',
        highlightthickness=0)
        self.__initialize(width,notes,font,markcolor,fg,markbg)
    
    def __get_endy(self):
        bbox=self.bbox('all')
        if bbox:
            return bbox[3]
        else:
            return 5
        
    def __initialize(self,width,notes,font,markcolor,fg,markbg):
        for i in notes:
            self.create_text((7,self.__get_endy()),text=i,font=font,fill=fg,anchor='nw',width=width-14)
        bbox=self.bbox('all')
        back=self.create_polygon((bbox[0],5,width-2,5,width-2,bbox[3],bbox[0],bbox[3]),
        fill=markbg,outline=markbg,width=7)
        self.create_line((2,5,2,bbox[3]),fill=markcolor,width=3,capstyle='round',joinstyle='round')
        self.lower(back)
        bbox=self.bbox('all')
        height=bbox[3]-bbox[1]
        self.config(height=height)


class TinTextTable(TinUI):
    #TinText的表格控件
    def __init__(self,master,width,bg='#fbfbfb',data=None,font=('微软雅黑',12)):
        super().__init__(master,update=False,width=width,bg=bg)
        table=self.add_table((2,2),data=data,font=font)
        bbox=list(self.bbox('all'))
        height=bbox[3]-bbox[1]+4
        bbox[2]+=2#宽度右侧留白
        bbox[3]+=2#高度底部留白
        self.config(scrollregion=bbox,width=width,height=height)
    

class TinTextPartAskFrame(ttk.Frame):
    #TinText<part>询问框
    def __init__(self,master,name):
        super().__init__(master.frame)
        self.master=master
        self.partname=name
        self.result=None
        self.tinui=BasicTinUI(self,bg=master.cget('background'))
        self.tinui.pack(fill='both',expand=True)
    
    def initial(self):
        w,h=self.master.winfo_width(),self.master.winfo_height()
        self.place(x=w/2,y=h,width=w,height=60,anchor='s')

        self.tinui.add_paragraph((5,w/2),text=f'是否阅读 {self.partname} ?')
        bbox=self.tinui.bbox('all')
        endy=bbox[3]+3
        self.tinui.add_button2((w/2-2,endy),minwidth=w/2-14,text='YES',command=self.yes,anchor='ne')
        self.tinui.add_button2((w/2+2,endy),minwidth=w/2-14,text='NO',command=self.no,anchor='nw')
        bbox=self.tinui.bbox('all')
        self.tinui.config(scrollregion=bbox)

        self.grab_set()
        self.wait_window(self)

        return self.result

    def yes(self,e):
        self.result=True
        self.destroy()
    
    def no(self,e):
        self.result=False
        self.destroy()