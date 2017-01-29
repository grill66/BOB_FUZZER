import fuzzer
from misc import *


def main():
    print "****** FUZZER ******"\

    PrintLog("[*] Creating Class Object...")

    _fuzzer = fuzzer.fuzzer()
    PrintLog("done.\n")

    PrintLog("[*] Reading Config file...")
    _fuzzer.ReadConfig()
    PrintLog("done.\n")

    PrintLog("[*] Starts Fuzzing...!\n")
    _fuzzer.Fuzz()




if __name__ == "__main__":
    main()