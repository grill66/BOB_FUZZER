import misc
import proc_manager


import os
import random
import threading
from time import sleep
from math import log
from shutil import copy

# Mutation Type, seedfile name,

FULLY_RANDOMIZED_FUZZER = 0x0



MONITOR_NOT_RUNNING = 0x0
MONITOR_RUNNING     = 0x1


MUTATION_BYTE_TABLE = ""


for i in range (0, 0x100):
    tmp = "%02x" % i
    MUTATION_BYTE_TABLE = MUTATION_BYTE_TABLE + tmp.decode("hex")


class mutation():

    def __init__(self, input_file_stream,  work_dirname, input_file_name, fixed_offset_list, mutation_block_size ):

        self.exe_name = ""
        self.input_file_name = input_file_name
        self.input_file_stream = input_file_stream
        self.work_dirname = work_dirname
        self.fixed_offset_list = fixed_offset_list
        self.mutated_filename = ""
        self.mut_result_stream = ""

###     @exe_name               : Absolute path and exe name of executable
###     @input_file_name        : Absolute path of input file. input_file_name is the target file for mutation.
###     @input_file_stream      : File stream of input file.
###     @work_dirname           : Working directory-name on which mutation task would be processed.
###     @fixed_offset_list      : Offset list. File data within these offsets should be "UNCHANGED" after mutation.
###                               This option can be set via editing config.JSON file at home directory of fuzzer
###     @mutated_filename       : File name of mutated result file.
###     @mutated_result_stream  : File stream of mutated result file(string).


        self.waitseconds = None
        self.mut_block_size         = mutation_block_size
        self.mut_chunk_list         = []
        self.mutatable_check_list   = []
        self.mut_apply_list         = []

###     @waitseconds            : Maximum wait-seconds for checking crash
###     @mut_block_size         : Mutation unit block size
###     @mut_chunk_list         :
        self.minimize_hit = False
        self.monitor_status = MONITOR_NOT_RUNNING
        self.crash_dirname = ""



        return


    def FullyRandomizedMutation(self):
        misc.PrintLog("Fully-Randomized Mutation...")

        self.mut_result_stream = ""

        self.mut_apply_list = []

        self.MutateChunkList()

        # Saves Mutated file
        self.mutated_filename = misc.GetMD5HashFromString(self.mut_result_stream) + '.' + self.input_file_name.split('.')[-1]
        with open(self.work_dirname + self.mutated_filename, "wb") as f:
            f.write(self.mut_result_stream)

        return

    def MutateChunkList(self):
        # Mutate each chunk in mut_chunk_list
        for i in range(0, len(self.mut_chunk_list)):
            if self.mutatable_check_list[i] == True and random.randint(0, 1) == 1:
                # Mutate and Add
                self.mut_result_stream += self.MutateData(self.mut_chunk_list[i])
                self.mut_apply_list += [True]   # mutation is applied

            else:   # mutation is not applied
                self.mut_result_stream += self.mut_chunk_list[i]
                self.mut_apply_list += [False]
        return


    def DevideStreamIntoChunks(self):
###     Devide Stream and adds devided stream to chunk list
###     chunk : mutation unit. it consists of string
###     @mutatable_chunk_list[i] => Is mut_chunk_list[i] is mutatable?? It has True or False.

        if self.fixed_offset_list == []:
            self.AddMutationBlockToList(self.input_file_stream)
            return
        else:
            curoffset = 0
            for i in range(0, len(self.fixed_offset_list)):
            ### Avoid mutating fixed offset

                self.AddMutationBlockToList(self.input_file_stream[ curoffset : self.fixed_offset_list[i]["start"]])

                self.mut_chunk_list += [ self.input_file_stream[self.fixed_offset_list[i]["start"]:self.fixed_offset_list[i]["end"] + 1] ]
                self.mutatable_check_list += [False]

                curoffset = self.fixed_offset_list[i]["end"] + 1

            # Add rest into chunk list
            self.AddMutationBlockToList(self.input_file_stream[curoffset:])


            return

    def AddMutationBlockToList(self, stream):
###     Usually called by DevideStream function.
###     It devides passed parameter stream into several blocks
###     Block-size of each chunk is specified at config.JSON file.
###     @mut_chunk_list : This list will contain several chunks of stream

        curoffset = 0
        streamsize = len(stream)

        if streamsize <= self.mut_block_size:
            self.mut_chunk_list         = self.mut_chunk_list + [stream[curoffset:]]
            self.mutatable_check_list   = self.mutatable_check_list + [True]

            return

        else:
            while curoffset + self.mut_block_size + 1 < streamsize:
                self.mut_chunk_list         = self.mut_chunk_list + [ stream[curoffset:curoffset + self.mut_block_size] ]
                self.mutatable_check_list   = self.mutatable_check_list + [True]
                curoffset += self.mut_block_size

            self.mut_chunk_list         = self.mut_chunk_list + [ stream[curoffset:] ]
            self.mutatable_check_list   = self.mutatable_check_list + [True]

        return

    def MutateData(self, string):

        result = string

        #result = "".join(i if random.randint(0, 3) != 0 else MUTATION_BYTE_TABLE[random.randint(0, 0xff)] for i in string)
        #return result

        if len(string) < 10:
            mut_number = random.randint(0, len(string))
        else:
            mut_number = mut_number = random.randint(0, len(string) / 10)

        mut_idx_list = random.sample( range(0, len(string) - 1),  mut_number)

        for idx in mut_idx_list: #idx - 1 is mutation target offset
            result = string[:idx] + MUTATION_BYTE_TABLE[random.randint(0, 0xff)] + string[idx + 1:]


        return result

    def DeleteMutatedFile(self):
### Delete mutation result file
        os.remove(self.work_dirname + self.mutated_filename)
        return


    def Minimize(self):

### This function minimizes mut_result_stream

        self.min_stream = self.mut_result_stream
        curoffset = 0

        self.proc_dbg_class = proc_manager.debugger()
        self.proc_dbg_class.exe_name = self.exe_name
        self.proc_dbg_class.argument = self.work_dirname + "min" + '.' +self.input_file_name.split('.')[-1]
        print ""

        for i in range(len(self.mut_apply_list)):
        #for i in range(0, 4):
            #print len(self.mut_apply_list)
            #print len(self.mut_chunk_list)
            print "chunk len : %d, curoffset : %d" % (len(self.mut_chunk_list[i]), curoffset)
            if self.mut_apply_list[i] == True:
                # Throw restored file
                cur_restored_offset = curoffset + len(self.mut_chunk_list[i])
                #print "cur_restored_offset : %d" % cur_restored_offset
                self.min_stream = self.min_stream[:curoffset]+ self.input_file_stream[curoffset:cur_restored_offset] + self.min_stream[cur_restored_offset:]
                #print threading.activeCount()
                while True:
                    try:
                        #print "opening"
                        min_fp = open(self.work_dirname + "min" + '.' +self.input_file_name.split('.')[-1], "wb")
                        break
                    except:
                        sleep(1)
                        pass
                min_fp.write(self.min_stream)
                min_fp.close()

                self.CheckCrash()   # check if minimized file cause crash

                # TODO: self.minimize_hit <= Is it hit??
                if self.minimize_hit == True:
                    curoffset += len(self.mut_chunk_list[i])
                    print "Minimize hit... adding this chunk...", curoffset

                else:
                    print "[*] Minimize missed", curoffset
                    #print self.input_file_stream[curoffset:curoffset + 10]
                    #print ""
                    #print self.mut_result_stream[curoffset:curoffset + 10]

                    self.MinimizeChunk(self.mut_chunk_list[i], curoffset) #curoffset : start offset of chunk
                    self.min_stream = self.min_stream[:curoffset] + self.mut_result_stream[curoffset:]

                    #print self.min_stream[curoffset:curoffset + 10]

                    curoffset += len(self.mut_chunk_list[i])

                    #print self.input_file_stream[:curoffset]


            else:   # If current chunk is not mutated...
                curoffset += len(self.mut_chunk_list[i])
                print "[*] Not Mutated chunk...", curoffset

        # Minimize done...
        copy(self.work_dirname + "min." + self.mutated_filename.split('.')[-1],
             "crashes\\" + self.crash_dirname + "\\" + self.mutated_filename.split('.')[0]
             + "_minimized." + self.mutated_filename.split('.')[-1])


        self.mut_apply_list = []
        self.mut_result_stream = None

        return


    def CheckCrash(self):
### It checks if minimized file caused crash

        dbg_thread = threading.Thread(target=self.proc_dbg_class.ExecuteProcess)
        dbg_thread.setDaemon(0)
        dbg_thread.start()

        sleep(1)

        monitor_thread = threading.Thread(target = self.MinimizeMonitor)
        monitor_thread.setDaemon(0)
        monitor_thread.start()

        while self.proc_dbg_class.DBG_status != proc_manager.DBG_NOT_RUNNING or self.monitor_status != MONITOR_NOT_RUNNING:
            sleep(1)
        #print threading.activeCount()
        return


    def MinimizeChunk(self, input_block, chunk_offset):
    #   Minimize input_block. chunk_offset is start offset of input_block in mutated file

        input_len = len(input_block)
        block_size = pow(4, int(log(len(input_block) - 1, 4)))  # block size is 4^n

        if block_size <= 4:
            #print "blk size <= 4"
            return

        else:
            curoffset = 0

            while curoffset + block_size + 1 < input_len:
                # print curoffset
                self.min_stream = self.min_stream[:chunk_offset + curoffset] \
                                  + self.input_file_stream[chunk_offset + curoffset:chunk_offset + curoffset + block_size]\
                                  + self.min_stream[chunk_offset + curoffset + block_size:]

                while True:
                    try:
                        min_fp = open(self.work_dirname + "min" + '.' + self.input_file_name.split('.')[-1], "wb")
                        break
                    except:
                        sleep(1)
                        pass
                min_fp.write(self.min_stream)
                min_fp.close()

                self.CheckCrash()


                if self.minimize_hit:
                    print "[*] block minimize hit. curoffset : %d" % (curoffset + chunk_offset)
                    curoffset += block_size
                else:
                    print "[*] block minimize miss. curoffset : %d" % (curoffset + chunk_offset)
                    self.min_stream = self.min_stream[:chunk_offset + curoffset] \
                                  + self.mut_result_stream[chunk_offset + curoffset:chunk_offset + curoffset + block_size]\
                                  + self.min_stream[chunk_offset + curoffset + block_size:]

                    self.MinimizeChunk(self.min_stream[chunk_offset + curoffset:chunk_offset + curoffset + block_size],
                                       chunk_offset + curoffset)
                    curoffset += block_size


            if curoffset < chunk_offset + input_len: # check rest string...

                self.min_stream = self.min_stream[:chunk_offset + curoffset] \
                                  + self.input_file_stream[chunk_offset + curoffset:chunk_offset + input_len]\
                                  + self.min_stream[chunk_offset + curoffset + block_size:]

                while True:
                    try:
                        min_fp = open(self.work_dirname + "min" + '.' + self.input_file_name.split('.')[-1], "wb")
                        break
                    except:
                        sleep(1)
                        pass
                min_fp.write(self.min_stream)
                min_fp.close()

                self.CheckCrash()


                if self.minimize_hit:
                    print "[*] Block minimize hit. curoffset : %d" % (curoffset + chunk_offset)
                    curoffset += block_size
                else:
                    print "[*] Block minimize miss. curoffset : %d" % (curoffset + chunk_offset)
                    self.min_stream = self.min_stream[:chunk_offset + curoffset] \
                                  + self.mut_result_stream[chunk_offset + curoffset:chunk_offset + input_len]\
                                  + self.min_stream[chunk_offset + input_len:]

                    self.MinimizeChunk(self.min_stream[chunk_offset + curoffset:chunk_offset + curoffset + block_size],
                                       chunk_offset + curoffset)
                    curoffset += block_size
            else:
                # There's no rest block
                return

        return

    def MinimizeMonitor(self):
        self.monitor_status = MONITOR_RUNNING

        sleep(self.waitseconds)

        if self.proc_dbg_class.DBG_status < proc_manager.CRASH_OCCURED:    # If crash is not occured...
            print "[*] Minimization missed..."
            self.minimize_hit = False
            try:
                self.proc_dbg_class.dbg.terminate_process()
            except :
                pass

            self.targetpid = None
            self.proc_dbg_class.DBG_status = proc_manager.DBG_NOT_RUNNING

        else:
            print "[*] Minimization catch..."
            self.minimize_hit = True
            self.proc_dbg_class.DBG_status  = proc_manager.DBG_NOT_RUNNING


        self.monitor_status = MONITOR_NOT_RUNNING

        return

    def __del__(self):
        return


