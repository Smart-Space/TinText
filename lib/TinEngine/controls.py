"""
TinText内部控件
"""
import tkinter as tk
from PIL import Image,ImageTk
from TinUI import BasicTinUI, TinUIXml


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
    def __init__(self,tintext,width,color) -> None:
        super().__init__(master=tintext,width=width,bg=color,relief='flat',
        highlightthickness=0,height=2)

