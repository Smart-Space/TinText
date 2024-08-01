"""
gui.py
TinText的窗口管理
"""
from lib.structure import Functions
from lib.gui import reader, writer

reader_functions=Functions()

writer_functions=Functions()
writer_functions.start=writer.start

#TinReader
def start_reader(quit):
    reader.start(quit,writerfuncs=writer_functions)

def start_reader_with_file(filename,quit):
    reader.start_with_file(filename,quit,writerfuncs=writer_functions)

#TinWriter
# def initial_writer():
#     writer.initial(reader.reopenfile)