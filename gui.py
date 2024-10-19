"""
gui.py
TinText的窗口管理
"""
from lib.structure import Functions
from lib.gui import reader, writer, maker

import process


reader_functions=Functions()

writer_functions=Functions()
writer_functions.start=writer.start
writer_functions.close=writer.close_writer

maker_functions=Functions()
maker_functions.start=maker.initial

#TinReader
def start_reader(quit):
    reader.start(quit,writerfuncs=writer_functions,makerfuncs=maker_functions)

def start_reader_with_file(filename,quit):
    reader.start_with_file(filename,quit,writerfuncs=writer_functions,makerfuncs=maker_functions)

#TinWriter
# def initial_writer():
#     writer.initial(reader.reopenfile)