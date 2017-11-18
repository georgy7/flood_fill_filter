# -*- coding: utf-8 -*-

# This file is released into the public domain.

# You may use it under the terms of the Unlicense.
# For more information, please refer to <http://unlicense.org/>

# Author: Georgy Ustinov


import sys
import time
import numpy as np

def prepare_stream(s):
    PY3K = sys.version_info >= (3, 0)
    if PY3K:
        return s.buffer
    else:
        if sys.platform == "win32":
            import os, msvcrt
            msvcrt.setmode(s.fileno(), os.O_BINARY)
        return s

def log(o):
    sys.stderr.write(str(o) + "\n")

def prepare_streams():
    import struct
    input = prepare_stream(sys.stdin)
    output = prepare_stream(sys.stdout)
    x_raw = input.read(4)
    y_raw = input.read(4)
    x = struct.unpack('i', x_raw)[0]
    y = struct.unpack('i', y_raw)[0]
    output.write(x_raw)
    output.write(y_raw)
    return input, output, x, y

def read_image(input, x, y):
    buf = input.read(4 * 4 * x * y)
    pixels = np.frombuffer(buf, dtype = np.dtype('<f'))
    pixels = pixels.reshape(y, x, 4)
    return pixels

class Start:
    def __init__(self):
        self.input, self.output, self.x, self.y = prepare_streams()
        self.start_time = time.time()
        self.pixels = read_image(self.input, self.x, self.y)
        self.result = np.zeros((self.y, self.x, 4), dtype = np.dtype('<f'))

    def end(self):
        b = self.result.astype('<f').tobytes()
        sys.stdout.buffer.write(b)
        end_time = time.time()
        log(end_time - self.start_time)

