import misc

import os
import random

# Mutation Type, seedfile name,

FULLY_RANDOMIZED_FUZZER = 0x0
XML_FUZZER              = 0x1

class mutation():

    def __init__(self, input_file_stream, mut_type, work_dirname, input_file_name, fixed_offset_list, mutation_block_size ):

        self.input_file_stream = input_file_stream
        self.mut_type = mut_type
        self.input_file_apspath = os.path.abspath(input_file_name)
        self.work_dirname = work_dirname
        self.fixed_offset_list = fixed_offset_list
        self.input_file_name = input_file_name

        self.mutated_filename = ""
        self.mut_result_stream = ""

        self.mutation_block_size = mutation_block_size
        self.mutation_chunk_list = []
        self.mutatable_check_list = []
# @stream               : File stream of seed file.
# @mut_type             : Mutation type of
# @seed_name            : Absolute path of seed file.
# @work_dirname         : Working directory-name on which mutation task would be processed.
# @fixed_offset_list    : offset list. File data within these offsets should be unchanged after mutation. This option can be set via editing config.JSON file at home directory of fuzzer

        return


    def FullyRandomizedMutation(self):
        misc.PrintLog("Fully-Randomized Mutation...")

        self.mut_result_stream = ""


        # TODO : Complete muation process...
        # DevideStreamIntoChunks => makes mutation_chunk_list and mutatable_chunk_list
        # MutateChunkList => Mutate Each Chunk and concatenate them
        #



        # Saves Mutated file
        self.mutated_filename = misc.GetMD5HashFromString(self.mut_result_stream) + '.' + self.input_file_name.split('.')[-1]
        with open(self.work_dirname + "\\" + self.mutated_filename, "wb") as f:
            f.write(self.mut_result_stream)

        return

    def MutateChunkList(self):
        # Mutate each chunk in mutation_chunk_list
        for i in range(0, len(self.mutation_chunk_list)):
            if self.mutatable_check_list[i] == True:
                # Mutate and Add
                self.mut_result_stream += self.MutateData(self.mutation_chunk_list[i])
            else:
                self.mut_result_stream += self.mutation_chunk_list[i]
        return


    def DevideStreamIntoChunks(self):
        # Devide Stream
        # chunk :
        # @mutatable_chunk_list[i] => Is mutation_chunk_list[i] is mutatable?? It has True or False.

        if self.fixed_offset_list == []:
            self.AddMutationBlockToList(self.input_file_stream)

        else:
            for i in range(0, len(self.fixed_offset_list)):
                # TODO : avoid offset
                # devide
                # add fixed_offset chunk : mutatable = False
                return

        return


    def AddMutationBlockToList(self, stream):
        # Usually called by DevideStream function.
        # It devides passed parameter stream into several blocks
        # Block-size of each chunk is specified at config.JSON file.
        # @mutation_chunk_list : This list will contain several chunks of stream

        curoffset = 0
        streamsize = len(stream)

        if streamsize <= self.mutation_block_size:
            self.mutation_chunk_list = self.mutation_chunk_list + [stream[curoffset:]]
            self.mutatable_check_list = self.mutatable_check_list + [True]

            return

        else:
            while curoffset + self.mutation_block_size < streamsize:
                self.mutation_chunk_list = self.mutation_chunk_list + [ stream[curoffset:curoffset + self.mutation_block_size] ]
                self.mutatable_check_list = self.mutatable_check_list + [True]
                curoffset = curoffset + self.mutation_block_size

            self.mutation_chunk_list = self.mutation_chunk_list + [ stream[curoffset:] ]
            self.mutatable_check_list = self.mutatable_check_list + [True]

        return



    def MutateData(self, string):
        # (1) Addition
        # (2) Change
        # (3) Suppression
        result = "".join(i if random.randint(0, 1) else misc.MUTATION_BYTE_TABLE[random.randint(0, 0xff)] for i in string)
        return result

    def DeleteMutatedFile(self):
        os.remove(self.work_dirname + "\\" + self.mutated_filename)
        return


    def __del__(self):
        return


