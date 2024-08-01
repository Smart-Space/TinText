"""
/lib/process/thread.py
TinText的多线程管理
"""
from threading import Thread, Lock
from queue import Queue
from concurrent.futures import ThreadPoolExecutor
