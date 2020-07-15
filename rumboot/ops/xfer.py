from rumboot.ops.base import base
import tqdm

class basic_uploader(base):
    formats = {
        "first_upload"      : "boot: host: Hit '{}' for X-Modem upload",
        "first_upload_basis"  : "boot: host: Hit 'X' for xmodem upload",
        "upload_uboot": "Trying to boot from UART"
        }

    def __init__(self, term):
        super().__init__(term)

    def sync(self, syncword):
        ser = self.term.ser
        if self.term.replay:
            return
        while True:
            ser.write(syncword.encode())
            while True:
                tmp1 = ser.read(1)
                tmp2 = ser.read(1)
                if tmp1 == b"C" and tmp2 == b"C": 
                    return
            break

    def action(self, trigger, result):
        if trigger != "upload_uboot" and self.term.xfer.how == "xmodem":
            self.sync("X")

        if not self.term.xfer.push(self.term.chip.spl_address):
            print("Upload failed")
            return 1
        return True



class runtime(basic_uploader):
    formats = {
        "runtime"           : "UPLOAD: {} to {:x}",
    }

    def action(self, trigger, result):
        arg = result[0]
        fl = self.term.plusargs[arg]
        stream = open(fl, 'rb')
        print("Sending %s via xmodem" % fl)
        ret = self.term.xfer.send(stream, result[1], "Uploading")
        stream.close()  
        return ret



class incremental(basic_uploader):
    formats = {
        "incremental_upload": "boot: host: Back in rom, code {}",
    }

    def action(self, trigger, result):
        ret = int(result[0])

        if ret != 0:
            return ret

        if self.term.next_binary(True) == None:
            print("No more files, exiting")
            return ret

        if (self.term.xfer.how == "xmodem"):
            self.sync("X")

        if not self.term.xfer.push(self.term.chip.spl_address):
            print("Upload failed")
            return 1
        return True

class flasher(basic_uploader):
    formats = {
        "flash_upload"      : "boot: Press '{}' and send me the image"
    }

    def action(self, trigger, result):
        self.term.xfer.selectTransport("xmodem-128")
        desc = "Writing image"
        self.sync("X")
        if not self.term.xfer.push(self.term.chip.spl_address):
            print("Upload failed")
            return 1
        return True