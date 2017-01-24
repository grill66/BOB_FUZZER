from misc import *
import mutation

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


class fuzzer():

    def __init__(self):

        self.exe_name = ""
        self.argument = ""
        self.iteration_per_seed = None

        self.seed_dirname = ""
        self.work_dirname = ""

        self.fixed_offset_list = []

        self.iteration = 0
        self.targetpid = None

        self.fuzzer_status = DBG_NOT_RUNNING
        self.inputfilename = ""
        self.inputfilepath = ""

        self.seed_stream = ""

        self.mut_class = None

        return

    def ReadConfig(self): # Read configuration from JSON format file

        self.exe_name               = GetValueFromConfigFile("exe_name")
        self.iteration_per_seed     = GetValueFromConfigFile("iteration_per_seed")
        self.seed_dirname           = GetValueFromConfigFile("seed_dirname")
        self.work_dirname           = GetValueFromConfigFile("work_dirname")
        self.fixed_offset_list      = GetValueFromConfigFile("fixed_offset_list")
        self.argument               = GetValueFromConfigFile("argument")
        self.waitseconds            = GetValueFromConfigFile("waitseconds")
        self.mut_type               = GetValueFromConfigFile("mut_type")
        self.mutation_block_size    = GetValueFromConfigFile("mutation_block_size")

        return

    def ErrorHandler(self, dbg):

        if dbg.dbg.u.Exception.dwFirstChance:
            return DBG_EXCEPTION_NOT_HANDLED

        print "Crash"

        self.fuzzer_status = CRASH_OCCURED

        ## Record Crash Information
        crash_bin = utils.crash_binning.crash_binning()
        crash_bin.record_crash(dbg)
        self.crash = crash_bin.crash_synopsis()

        curtime = datetime.datetime.today()
        crash_dirname = "[%d.%02d.%02d_%02d_%02d_%02d]" \
                          % (curtime.year, curtime.month, curtime.day, curtime.hour, curtime.minute, curtime.second)

        os.mkdir(".\\crashes\\" + crash_dirname)

        # Save Crash Info
        crashinfo_fp = open("crashes\\" + crash_dirname + "\\" + self.inputfilename + ".log", "w+")
        crashinfo_fp.write(self.crash)
        crashinfo_fp.close()

        # Save Crash-causing file
        shutil.copy(self.inputfilepath + self.inputfilename, "crashes\\" + crash_dirname + "\\" + self.inputfilename)

        self.dbg.terminate_process()
        self.fuzzer_status = DBG_NOT_RUNNING
        self.targetpid = None

        return DBG_EXCEPTION_NOT_HANDLED

    def ProcessDebugger(self):

        self.fuzzer_status = DBG_RUNNING
        self.dbg = pydbg()

        self.dbg.set_callback(EXCEPTION_ACCESS_VIOLATION, self.ErrorHandler)
        #self.dbg.get_debug_privileges()

        self.dbg.load(self.exe_name, self.argument)

        self.targetpid = self.dbg.pid
        self.dbg.run()
        return

    def CrashChecker(self):

        time.sleep(self.waitseconds)

        if self.fuzzer_status != CRASH_OCCURED:
            self.dbg.terminate_process()
            self.pid = None
            self.fuzzer_status = DBG_NOT_RUNNING

        else:
            print "[*] Crash Analyzing..."
            while self.fuzzer_status == CRASH_OCCURED:
                time.sleep(1)

        # TODO : restore below statement - Delete mutated-file
        # self.mut_class.DeleteMutatedFile()

        self.mut_class = None
        return

    def Fuzz(self):
        while True:

            PrintLog("[*] Selecting seed file...\n")
            seed_filename = self.SelectSeed()

            seed_abspath = self.seed_dirname + "\\" + seed_filename
            self.seed_stream = GetStream(seed_abspath)

            for i in range(0, self.iteration_per_seed):
                PrintLog("[*] Starting Fuzz Cycle(Itration : %d)\n" % self.iteration)
                self.FuzzCycle(seed_abspath)

    def FuzzCycle(self, seed_filename):
        while True:
            if self.fuzzer_status == DBG_NOT_RUNNING:
                PrintLog("[*] Mutating File : ")

                self.mut_class = mutation.mutation(self.seed_stream, self.mut_type, self.work_dirname, seed_filename, self.fixed_offset_list)
                self.mut_class.FullyRandomizedMutation()

                inputfilename = self.mut_class.mutated_filename
                PrintLog(inputfilename)
                PrintLog(" done.\n")
                PrintLog("[*] Starting debugger...\n")

                # TODO : Revise - improve flexibiliy
                self.argument = self.work_dirname + "\\" + self.mut_class.mutated_filename

                dbg_thread = threading.Thread(target = self.ProcessDebugger)
                dbg_thread.setDaemon(0)
                dbg_thread.start()

                while self.targetpid == None:
                    time.sleep(1)

                check_thread = threading.Thread(target = self.CrashChecker)
                check_thread.setDaemon(0)
                check_thread.start()

                self.iteration = self.iteration + 1

                return
            else:
                time.sleep(self.waitseconds)

    def SelectSeed(self):
        seedlist = os.listdir(self.seed_dirname)
        return seedlist[random.randint(0, len(seedlist) - 1)]

    def __del__(self):
        return