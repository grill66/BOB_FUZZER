
def DevideStream(stream, mutation_chunk_list):
    curoffset = 0
    streamsize = len(stream)
    if fixed_offset_list == []:
        while curoffset + mutation_block_size <= streamsize:
            mutation_chunk_list = mutation_chunk_list + [ stream[curoffset:curoffset + mutation_block_size] ]
            curoffset = curoffset + mutation_block_size

        mutation_chunk_list = mutation_chunk_list + [ stream[curoffset:] ]

    else:

        return


    return mutation_chunk_list

def DevideMutationBlock():

    return


mutation_block_size = 1024

mutation_chunk_list = []

fixed_offset_list = []

afixed_offset_list = [
    {
        "start" : 256,
        "end"   : 512
    },
    {
        "start" : 1024 + 256,
        "end"   : 1024 + 512
    }
]


fp = open("C:\\Users\\user\\Desktop\\crash.cell", "rb")
stream = fp.read()
fp.close()







result = DevideMutationBlock(stream, mutation_chunk_list)

print 1
#print result[0]
print 2
#print result[1]

print "a"
print result[-1]


