import misc

import os
import random

# Mutation Type, seedfile name,

FULLY_RANDOMIZED_FUZZER = 0x0
XML_FUZZER              = 0x1

class mutation():

    def __init__(self, input_file_stream, mut_type, work_dirname, input_file_name, fixed_offset_list ):

        self.input_file_stream = input_file_stream
        self.mut_type = mut_type
        self.input_file_apspath = os.path.abspath(input_file_name)
        self.work_dirname = work_dirname
        self.fixed_offset_list = fixed_offset_list
        self.input_file_name = input_file_name

        self.mutated_filename = ""
        self.mut_result_stream = ""

        # @stream               : File stream of seed file.
        # @mut_type             : Mutation type of
        # @seed_name            : Absolute path of seed file.
        # @work_dirname         : Working directory name on which mutation task would be processed.
        # @fixed_offset_list    : offset list that should be unchanged after mutation. it can be set via editing config.JSON file at home directory of fuzzer

        return


    def FullyRandomizedMutation(self):
        misc.PrintLog("Fully-Randomized Mutation...")

        self.mut_result_stream = ""

        # Mutation
        curoffset = 0
        for idx in range(0, len(self.fixed_offset_list)):

            self.mut_result_stream = self.mut_result_stream + self.MutateData(self.input_file_stream[curoffset:self.fixed_offset_list[idx]["start"]]) \
                                     + self.input_file_stream[self.fixed_offset_list[idx]["start"]:self.fixed_offset_list[idx]["end"] + 1]

            curoffset = self.fixed_offset_list[idx]["end"] + 1

        self.mut_result_stream = self.mut_result_stream + self.MutateData(self.input_file_stream[curoffset:])

        # Saves Mutated file


        self.mutated_filename = misc.GetMD5HashFromString(self.mut_result_stream) + '.' + self.input_file_name.split('.')[-1]

        fp = open(self.work_dirname + "\\" + self.mutated_filename, "wb")
        fp.write(self.mut_result_stream)
        fp.close()

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


