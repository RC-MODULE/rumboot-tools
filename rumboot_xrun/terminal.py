import serial
import sys
from xmodem import XMODEM
import os
from parse import parse
import time
import io
from tqdm import tqdm

class terminal:
        verbose=True
        logstream=None

        def __init__(self, port, speed):
            self.port = port
            self.ser = serial.Serial(port, speed, timeout=1)
            def getc(size, timeout=10):
                ret = self.ser.read(size)
                return ret or None
            def putc(data, timeout=10):
                return self.ser.write(data)  # note that this ignores the timeout
            self.modem = XMODEM(getc, putc)

        def log(self, *args, **kwargs):
            if self.verbose:
                tqdm.write(*args, **kwargs)
            if not self.logstream == None:
                self.logstream.write(*args)

        def loop(self, exitfmt="boot: host: Back in rom, code {}"):
            while True:
                ret = None
                line = self.ser.readline()
                try: 
                    line = line.decode()
                    self.log(line, end='')
                    ret = parse(exitfmt, line)
                except:
                    pass

                if ret:
                   code = ret[0]
                   return int(code)

        def poll_for_invite(self, welcome, shortsync=False):
            while True:
                line = self.ser.readline()
                l = line.decode(errors='replace')
                self.log(l,end='')
                if (line == welcome):
                    self.ser.write("X".encode())
                    if shortsync:
                        break
                    while True:
                        tmp1 = self.ser.read(1)
                        tmp2 = self.ser.read(1)
                        if tmp1 == b"C" and tmp2 == b"C": 
                            break
                    break

        def xmodem_send(self, fl, chunksize=0, desc="Uploading file", welcome=b"boot: host: Hit 'X' for xmodem upload\n"):
            stream = open(fl, 'rb')
            return self.xmodem_send_stream(stream, chunksize, welcome, desc)

        def stream_size(self, stream):
            stream.seek(0,2)
            len = stream.tell()
            stream.seek(0)
            return len

        def xmodem_send_stream(self, stream, chunksize=0, welcome=b"boot: host: Hit 'X' for xmodem upload\n", desc="Uploading stream"):
            self.poll_for_invite(welcome)
            pbar = tqdm(desc=desc, total=self.stream_size(stream), unit_scale=True, unit_divisor=1024, unit='B')

            def callback(total_packets, success_count, error_count):
                if success_count*128 < pbar.total:
                    pbar.update(128)
                else:
                    pbar.update(128 - (success_count*128 - pbar.total))
            
            stream.seek(0)
            if chunksize==0:
                ret = self.modem.send(stream, retry=16, callback=callback)
            else:
                while True:
                    data = stream.read(chunksize)
                    if (not data):
                            break
                    data = io.BytesIO(data)
                    ret = self.modem.send(data, retry=16, callback=callback)
                    self.poll_for_invite(welcome, True)           