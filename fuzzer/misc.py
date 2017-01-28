import sys

def PrintLog(str):
    sys.stdout.write(str)
    return


def BackSlashWrapper(str):
    if str[-1] != '\\':
        return str + '\\'
    return str

import json

def GetValueFromConfigFile(key):
    with open("config.JSON", "rb") as fp_config:
        config_data = json.load(fp_config)

        return config_data[key]


import hashlib

def GetMD5HashFromFile(file_name):
    hash = hashlib.md5()
    fp = open(file_name, "rb")

    for block in iter(lambda: fp.read(4096), b""):
        hash.updata(block)
    fp.close()

    return hash.hexdigest()

def GetMD5HashFromString(string):
    return hashlib.md5(string).hexdigest()


def GetStream(filename):
    fp = open(filename, "rb")
    stream = fp.read()
    fp.close()
    return stream




MUTATION_BYTE_TABLE = ""

for i in range (0, 0x100):
    tmp = "%02x" % i
    MUTATION_BYTE_TABLE = MUTATION_BYTE_TABLE + tmp.decode("hex")