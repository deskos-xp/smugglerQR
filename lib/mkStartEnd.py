import os,sys
lib='./lib'
sys.path.insert(0,lib)
import smuggler_lib

class mkEnds:
    def __init__(self):
        pass

    def mkCaps(self,scale=3):
        encoder=smuggler_lib.app_qr_handler()
        encoder.createQrCode(b'START',fname='START.png',scale=scale)
        encoder.createQrCode(b'STOP!',fname='END.png',scale=scale)

if __name__ == '__main__':
    app=mkEnds()
    app.mkCaps(scale=3)
