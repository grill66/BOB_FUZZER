from pydbg import *
from pydbg.defines import *




import utils
import time
import threading

#DBG thread status constants
DBG_NOT_RUNNING         = 0x0
DBG_RUNNING             = 0x1
CRASH_OCCURED           = 0x2
PROCESSING_CRASH        = 0x3


#Monitor thread status constants...

class debugger():
    def __init__(self):
        self.DBG_status     = DBG_NOT_RUNNING



        self.exe_name = ""
        self.argument = ""

        self.crash_bin  = None
        self.crash_info = ""

        self.targetpid = None

        return

    def ExceptionHandler(self, dbg):

        if dbg.dbg.u.Exception.dwFirstChance:
            return DBG_EXCEPTION_NOT_HANDLED

        print "[*] Crash...!!"

        self.DBG_status = CRASH_OCCURED

        ## Record Crash Information
        self.crash_bin = utils.crash_binning.crash_binning()
        self.crash_bin.record_crash(dbg)
        self.crash_info = self.crash_bin.crash_synopsis()

        self.dbg.terminate_process()
        self.DBG_status = PROCESSING_CRASH
        self.targetpid  = None

        return DBG_EXCEPTION_NOT_HANDLED


    def ExecuteProcess(self):
        self.DBG_status = DBG_RUNNING

        self.dbg = pydbg()
        self.dbg.set_callback(EXCEPTION_ACCESS_VIOLATION, self.ExceptionHandler)
        # self.dbg.get_debug_privileges()

        self.dbg.load(self.exe_name, self.argument)

        self.targetpid = self.dbg.pid
        self.dbg.run()
        return
