import misc
import proc_manager


import os
import random
import threading
import time

# Mutation Type, seedfile name,

FULLY_RANDOMIZED_FUZZER = 0x0
XML_FUZZER              = 0x1


MONITOR_NOT_RUNNING = 0x0
MONITOR_RUNNING     = 0x1



class mutation():

    def __init__(self, input_file_stream, mut_type, work_dirname, input_file_name, fixed_offset_list, mutation_block_size ):

        self.exe_name = ""

        self.input_file_stream = input_file_stream
        self.mut_type = mut_type
        self.input_file_apspath = os.path.abspath(input_file_name)
        self.work_dirname = work_dirname
        self.fixed_offset_list = fixed_offset_list
        self.input_file_name = input_file_name
        self.mutated_filename = ""

        self.mut_result_stream = ""

        self.waitseconds = None

        self.mut_block_size         = mutation_block_size
        self.mut_chunk_list         = []
        self.mutatable_check_list   = []
        self.mut_apply_list         = []
###     @stream               : File stream of seed file.
###     @mut_type             : Mutation type of
###     @seed_name            : Absolute path of seed file.
###     @work_dirname         : Working directory-name on which mutation task would be processed.
###     @fixed_offset_list    : offset list. File data within these offsets should be unchanged after mutation. This option can be set via editing config.JSON file at home directory of fuzzer

        self.minimize_hit = False

        return


    def FullyRandomizedMutation(self):
        misc.PrintLog("Fully-Randomized Mutation...")

        self.mut_result_stream = ""

        self.mut_apply_list = []



        # TODO : Complete muation process...
###     DevideStreamIntoChunks => makes mut_chunk_list and mutatable_chunk_list
###     MutateChunkList => Mutate Each Chunk and concatenate them
###
        #self.DevideStreamIntoChunks()
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
                # TODO : avoid offset
                # Add stream curoffset to fixed_offset_list[i]["start"] into chunk list...
                #print curoffset
                self.AddMutationBlockToList(self.input_file_stream[ curoffset : self.fixed_offset_list[i]["start"]])

                self.mut_chunk_list += [ self.input_file_stream[self.fixed_offset_list[i]["start"]:self.fixed_offset_list[i]["end"] + 1] ]
                self.mutatable_check_list += [False]

                curoffset = self.fixed_offset_list[i]["end"] + 1

            # Add rest into chunk list
            self.AddMutationBlockToList(self.input_file_stream[curoffset:])
            #print "\n", len(self.mutatable_check_list)
            #print self.mutatable_check_list

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
                #print curoffset
                self.mut_chunk_list         = self.mut_chunk_list + [ stream[curoffset:curoffset + self.mut_block_size] ]
                self.mutatable_check_list   = self.mutatable_check_list + [True]
                curoffset += self.mut_block_size

            self.mut_chunk_list         = self.mut_chunk_list + [ stream[curoffset:] ]
            self.mutatable_check_list   = self.mutatable_check_list + [True]

        return

    def MutateData(self, string):
        # (1) Addition
        # (2) Change
        # (3) Compression
        # TODO : restore mutation logic
        #result = string
        result = "".join(i if random.randint(0, 1) else misc.MUTATION_BYTE_TABLE[random.randint(0, 0xff)] for i in string)
        return result

    def DeleteMutatedFile(self):
### Delete mutation result file
        os.remove(self.work_dirname + self.mutated_filename)
        return


    def Minimize(self):
        self.min_stream = self.mut_result_stream
        curoffset = 0
        self.dbg = proc_manager.debugger()
        self.dbg.exe_name = self.exe_name
        self.dbg.argument = self.work_dirname + "min" + '.' +self.input_file_name.split('.')[-1]



        for i in range(len(self.mut_apply_list)):
            print len(self.mut_apply_list)
            print len(self.mut_chunk_list)

            if self.mut_apply_list[i] == True:
                # Throw restored file
                self.min_stream = self.input_file_stream[:curoffset] + self.mut_result_stream[curoffset:]

                min_fp = open(self.work_dirname + "min" + '.' +self.input_file_name.split('.')[-1], "wb")
                min_fp.write(self.min_stream)
                min_fp.close()

                self.CheckCrash()

                # TODO: self.minimize_hit <= Is it hit??
                if self.minimize_hit == True:
                    curoffset += len(self.mut_chunk_list[i])
                    print curoffset

                else:
                    return

            else:   # If current chunk is not mutated...
                curoffset += len(self.mut_chunk_list[i])
                print curoffset

        return


    def CheckCrash(self):
        dbg_thread = threading.Thread(target=self.dbg.ExecuteProcess)
        dbg_thread.setDaemon(0)
        dbg_thread.start()


        time.sleep(1)

        monitor_thread = threading.Thread(target = self.MinimizeMonitor)
        monitor_thread.setDaemon(0)
        monitor_thread.start()

        while self.dbg.DBG_status != self.dbg.DBG_NOT_RUNNING or self.monitor_status != MONITOR_NOT_RUNNING:
            time.sleep(1)

        return


    def MinimizeChunk(self, chunk, size):


        return

    def MinimizeMonitor(self):
        self.monitor_status = MONITOR_RUNNING

        time.sleep(self.waitseconds)

        if self.DBG_status < proc_manager.CRASH_OCCURED:    # If crash is not occured...
            print "[*] Minimization missed..."
            self.minimize_hit = False
            try:
                self.dbg.terminate_process()
            except :
                pass

            self.targetpid = None
            self.DBG_status = proc_manager.DBG_NOT_RUNNING

        else:
            print "[*] Minimizaion catch..."

            self.minimize_hit = True


            self.dbg.DBG_status  = proc_manager.DBG_NOT_RUNNING


        self.monitor_status = MONITOR_NOT_RUNNING
        return




    def __del__(self):
        return


