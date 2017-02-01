from misc import *
import mutation
import proc_manager


from pydbg import *
from pydbg.defines import *

import threading
import utils
import datetime
import os
import shutil
import time
import random


# Fuzzer status constants
DBG_NOT_RUNNING     = 0x0
DBG_RUNNING         = 0x1
CRASH_OCCURED       = 0x2
PROCESSING_CRASH    = 0x3


MONITOR_NOT_RUNNING = 0x0
MONITOR_RUNNING     = 0x1


class fuzzer(proc_manager.debugger):    # Inherit class from proc_manager.py

    def __init__(self):

        self.exe_name = ""
        self.argument = ""
        self.iteration_per_seed = None

        self.seed_dirname = ""
        self.work_dirname = ""

        self.fixed_offset_list = []

        self.iteration = 0
        self.targetpid = None

        self.DBG_status         = DBG_NOT_RUNNING
        self.monitor_status     = MONITOR_NOT_RUNNING

        self.seed_stream = ""

        self.mut_class = None
        self.need_minimize = False

        return

    def ReadConfig(self): # Read configuration from JSON format file

        self.exe_name               = GetValueFromConfigFile("exe_name")
        self.iteration_per_seed     = GetValueFromConfigFile("iteration_per_seed")
        self.seed_dirname           = BackSlashWrapper(GetValueFromConfigFile("seed_dirname"))
        self.work_dirname           = BackSlashWrapper(GetValueFromConfigFile("work_dirname"))
        self.fixed_offset_list      = GetValueFromConfigFile("fixed_offset_list")
        self.argument               = GetValueFromConfigFile("argument")
        self.waitseconds            = GetValueFromConfigFile("waitseconds")
        self.mut_type               = GetValueFromConfigFile("mut_type")
        self.mutation_block_size    = GetValueFromConfigFile("mutation_block_size")

        return


    def DebuggerMonitor(self):

        self.monitor_status = MONITOR_RUNNING

        # Wait crash for wait-seconds...
        time.sleep(self.waitseconds)

        if self.DBG_status < CRASH_OCCURED:    # If crash is not occured...
            try:
                self.dbg.terminate_process() # dbg : Inherited from proc_manager
            except :
                pass

            self.targetpid = None
            self.DBG_status = DBG_NOT_RUNNING

        else:
            print "[*] Crash Analyzing..."
            while self.DBG_status == CRASH_OCCURED:
                time.sleep(1)


            # move mutated file to crashes
            curtime = datetime.datetime.today()
            crash_dirname = "[%d.%02d.%02d_%02d_%02d_%02d]" \
                            % (
                            curtime.year, curtime.month, curtime.day, curtime.hour, curtime.minute, curtime.second)

            PrintLog("[*] Saving crash...DIR : "+crash_dirname + "...")

            os.mkdir(".\\crashes\\" + crash_dirname)

            # Save Crash Info
            crashinfo_fp = open(
                "crashes\\" + crash_dirname + "\\" + self.mut_class.mutated_filename.split('.')[0] + ".log", "wb")
            crashinfo_fp.write(self.crash_info)

            crashinfo_fp.write("len chunk list : %d, apply list : %d\n" \
                               % (len(self.mut_class.mut_chunk_list), len(self.mut_class.mut_apply_list)))

            for i in self.mut_class.mut_apply_list:
                crashinfo_fp.write("%d, " % i)

            crashinfo_fp.close()

            # Save Crash-causing file
            shutil.copy(self.work_dirname + self.mut_class.mutated_filename,
                        "crashes\\" + crash_dirname + "\\" + self.mut_class.mutated_filename)
            self.mut_class.crash_dirname = crash_dirname

            PrintLog("done\n")


            self.DBG_status  = DBG_NOT_RUNNING
            self.need_minimize = True

        while True:
            try:
                self.mut_class.DeleteMutatedFile()
                break
            except WindowsError, e:
                #print e
                time.sleep(1)
                continue

        self.monitor_status = MONITOR_NOT_RUNNING
        return


    def Fuzz(self):
        while True:

            PrintLog("[*] Selecting seed file...\n")
            seed_filename = self.SelectSeed()

            seed_abspath = self.seed_dirname + seed_filename
            self.seed_stream = GetStream(seed_abspath)

            self.mut_class = mutation.mutation(self.seed_stream,
                                               self.mut_type,
                                               self.work_dirname,
                                               seed_abspath,
                                               self.fixed_offset_list,
                                               self.mutation_block_size)

            # Devide Stream into Chunks
            self.mut_class.DevideStreamIntoChunks()

            for i in range(0, self.iteration_per_seed):
                PrintLog("[*] Starting Fuzz Cycle (Itration : %d)\n" % self.iteration)
                self.FuzzCycle(seed_abspath)

            self.mut_class = None

    def FuzzCycle(self, seed_filename):
        while True:
            if self.DBG_status == DBG_NOT_RUNNING and self.monitor_status == MONITOR_NOT_RUNNING:
                PrintLog("[*] Mutating File : ")

                #self.mut_class = mutation.mutation(self.seed_stream, self.mut_type, self.work_dirname, seed_filename, self.fixed_offset_list, self.mutation_block_size)
                self.mut_class.FullyRandomizedMutation()

                # TODO : Delete below statements...
                #self.mut_class.mut_apply_list = [0, 0, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 0, 0, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1]

                #f = open("C:\\Users\\user\\Desktop\\BOB_FUZZER\\fuzzer\\crashes\\[2017.01.29_20_37_57]\\crash.xls", "rb")
                #self.mut_class.mut_result_stream = f.read()
                #f.close()
                #self.mut_class.waitseconds = self.waitseconds
                #self.mut_class.exe_name = self.exe_name
                #self.mut_class.Minimize()

                #return
                # TODO : TO here

                PrintLog(self.mut_class.mutated_filename)
                PrintLog(" done.\n")
                PrintLog("[*] Starting debugger...\n")

                # TODO : Revise - improve flexibiliy
                self.argument = self.work_dirname + self.mut_class.mutated_filename

                debugger_thread = threading.Thread(target = self.ExecuteProcess)
                debugger_thread.setDaemon(0)
                debugger_thread.start()

                while self.targetpid == None:   # wait until debugger attaches to target process
                    time.sleep(1)

                monitor_thread = threading.Thread(target = self.DebuggerMonitor)
                monitor_thread.setDaemon(0)
                monitor_thread.start()

                self.iteration = self.iteration + 1
            else:
                break

        # Wait until DBG thread and monitor thread are terminated...
        while self.DBG_status >= DBG_RUNNING or self.monitor_status >= MONITOR_RUNNING:
            time.sleep(self.waitseconds)

        if self.need_minimize == True:
            # Minimize crash file...
            self.mut_class.waitseconds = self.waitseconds
            self.mut_class.exe_name = self.exe_name
            self.mut_class.Minimize()
            self.need_minimize = False

        return


    def SelectSeed(self):
    # Select Seed from seed directory.
    # It can be configured at config.JSON file.
        seedlist = os.listdir(self.seed_dirname)
        return seedlist[random.randint(0, len(seedlist) - 1)]

    def __del__(self):
        return