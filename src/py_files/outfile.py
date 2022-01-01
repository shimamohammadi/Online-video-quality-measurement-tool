from joblib import load
import sys
import os
import ctypes as ctypes
import ctypes.util

file1 = open("MyFile.264", "wb")
buffer = bytearray()
count = 0
batch_size = 1
batch = 100
width = 0
height = 0
index = 0
lst_nn = []
lst_img = []
lst_prediction = []
loaded_model = load("BBS.joblib.dat")
loaded_cs = load("BBS.joblib.cs")

__all__ = ['shdeny_read']

_SH_DENYRW = 0x10  # deny read/write mode
_SH_DENYWR = 0x20  # deny write mode
_SH_DENYRD = 0x30  # deny read
_S_IWRITE  = 0x0080  # for O_CREAT, a new file is not readonly

if sys.version_info[:2] < (3,5):
    _wsopen_s = ctypes.CDLL(ctypes.util.find_library('c'))._wsopen_s
else:
    _wsopen_s = ctypes.CDLL('api-ms-win-crt-stdio-l1-1-0')._wsopen_s

_wsopen_s.argtypes = (ctypes.POINTER(ctypes.c_int), # pfh
                      ctypes.c_wchar_p,             # filename
                      ctypes.c_int,                 # oflag
                      ctypes.c_int,                 # shflag
                      ctypes.c_int)                 # pmode


def shdeny_read(file, flags):
    fh = ctypes.c_int()
    err = _wsopen_s(ctypes.byref(fh),
                    file, flags, _SH_DENYRD, _S_IWRITE)
    if err:
        raise IOError(err, os.strerror(err), file)
    return fh.value


def file_write(bs, f, c, b):
    if bs == batch:
        f.write(b)
        f.close()
        f = open("MyFile{:04}.264".format(c), "wb", opener=shdeny_read)
        c += 1
        bs = 1
    else:
        f.write(b)
        bs += 1
    return bs, f, c

def proc_NN(input_list, width, height):
    #### Your Codes
    print(input_list)
    return 0