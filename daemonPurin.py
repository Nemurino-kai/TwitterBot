#!/usr/local/bin/python3.6

import purinAI
#import datetime
import sys
import traceback
from daemon import DaemonContext
from os     import path
#from time   import sleep
from lockfile.pidlockfile import PIDLockFile

import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

class BotDaemon:
    def __init__(self):
        self.basename = path.splitext(path.basename(__file__))[0]
        self.work_dir = path.dirname(path.abspath(__file__))

    def exec(self):
        try:
            dc = DaemonContext(
                working_directory = self.work_dir,
                pidfile = PIDLockFile("/tmp/{}.pid".format(self.basename)),
                stderr = open("{}.err".format(self.basename), "a+")
            )
            with dc:
                self.__do_process()
        except Exception as e:
            raise

    def __do_process(self):
        try:
            while True:
                purinAI.tweet()
        except Exception as e:
            raise

if __name__ == '__main__':
    try:
        obj = BotDaemon()
        obj.exec()
    except Exception as e:
        traceback.print_exc()
sys.exit(1)