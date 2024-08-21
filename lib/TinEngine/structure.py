"""
TinText结构相关部件
"""

class PartTag:
    """
    TinText <part> <pt> </part> </pt>
    """
    def __init__(self):
        self.names={'':True}
    
    def named(self,name):
        if name in self.names:
            return True
        else:
            return False

    def edit(self,name,state:bool):
        self.names[name]=state
    
    def delete(self,name):
        del self.names[name]
    
    def check(self):
        return self.names[tuple(self.names.keys())[-1]]
    
    def now(self):
        return tuple(self.names.keys())[-1]

    def clear(self):
        #删除除了''以外的所有值
        self.names.clear()
        self.names['']=True