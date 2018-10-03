#! /usr/bin/env python3

import os,sys,json
try:
    lib='./lib'
    sys.path.insert(0,lib)
except Exception as e:
    print(e)

import smuggler_lib

class doOne:
    def __init__(self):
        pass

    def mkpath(self,dir,fname):
        return os.path.join(dir,fname)

    def store_to_log(self,QR_fname,logfile='./results.json',resultdir='./results',skipDecode=False,decoded=None):
        #resultdir+logfile -> where data will be stored
        if skipDecode == False:
            decoder=smuggler_lib.app_qr_handler()
            decoded=decoder.decodeOneQrCode(QR_fname)
        elif skipDecode == True:
            if decoded != None:
                decoded=decoded
            else:
                exit('cannot use None value for decoded input when using skipDecode arg of store_to_log()')
        
        deformatter=smuggler_lib.reader()
        if len(decoded) > 1:
            print("multiple qr codes detected")
        for i in decoded:
            detes=[]
            detes.append(i)

            deformatted=deformatter.breakData(detes)
            formatted=deformatter.storeData(deformatted,returnChunk=True)

            path=self.mkpath(resultdir,logfile)
            logData=None

            if os.path.exists(path):
                with open(path,'r') as log:
                    logData=json.load(log)
                logData[formatted[0]]=formatted[1]
                with open(path,'w') as log:
                    json.dump(logData,log)
            else:
                with open(path,'w') as log:
                    json.dump(formatted[1],log)

if __name__ == "__main__":
    app=doOne()
    app.store_to_log(sys.argv[1],logfile='results.json',resultdir='./results')
