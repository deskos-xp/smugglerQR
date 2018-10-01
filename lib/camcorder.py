#! /usr/bin/env python3

import os,sys,cv2
import pyzbar.pyzbar as zbar
libs='./lib'
sys.path.insert(0,libs)
import smuggler_lib,handle_one

class camcorder:
    red='\033[1;31;40m'
    end='\033[1;40;m'
    green='\033[1;32;40m'
    yellow='\033[1;33;40m'
    other='\033[1;34;40m'
    blue='\033[1;35;40m'
    def __init__(self):
        pass
    def messages(self,code):
        if code not in [[],None]:
            code=code[0]
        try:
            data=code.data.decode().split(':')
            dataSTART='{0}{3}: {2}{1}'.format(self.green,data[1],self.end,'Data POS')
            dataEND='{0}{3}: {2}{1}'.format(self.red,data[-1],self.end,'Data Chunks')
            dataDocID='{0}{3}: {2}{1}'.format(self.blue,data[0],self.end,'Document ID')
            dataData='{0}{3}: {2}{1}'.format(self.other,data[2],self.end,'DataB64 String')
            data='\n'.join([dataSTART,dataEND,dataDocID,dataData])
            qtype='{0}{3}: {2}{1}'.format(self.yellow,code.type,self.end,'Code Type')
            print(qtype,data,sep='\n')
        except:
            e=sys.exc_info()
            print('{0}{1}{2}'.format(self.red,'something is not right with your code! {}'.format(e),self.end))
            print(code)

    def record(self,cam=0,qr_dir='camera-captures',displayCallback=None,result_dir='./results',logfile='results.json',saveFrame=False):
        if not os.path.exists(qr_dir):
            os.mkdir(qr_dir)
        lib=smuggler_lib.app_qr_handler()

        cap = cv2.VideoCapture(cam)
        while True:
            ret, frame = cap.read()
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2BGRA)
            if displayCallback == None:
                cv2.imshow('frame', rgb)
            else:
                displayCallback(frame)
            code=zbar.decode(rgb)
            if code != []:
                if code[0].type == 'QRCODE': 
                    self.messages(code)
                    try:
                        doOne=handle_one.doOne()
                        doOne.store_to_log('fake',resultdir=result_dir,decoded=code,skipDecode=True,logfile=logfile)
                        if saveFrame == True:
                            name=os.path.join(qr_dir,lib.mkdefaultName())
                            out=cv2.imwrite(name,frame)
                            print('{} : saved!'.format(name))
                    except:
                        e=sys.exc_info()
                        print('\033[1;31;40mrecording of QRCode Failed!:\033[1;40;m {}'.format(str(e)))
            
            key=cv2.waitKey(1)
            if key & 0xFF == ord('q'):
                break
            '''
            if key & 0xFF == ord('c'):
                name=os.path.join(qr_dir,lib.mkdefaultName())
                out = cv2.imwrite(name,frame)
                print('{} : captured!'.format(name))
            '''

        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    app=camcorder()
    app.record()
