#! /usr/bin/env python3
import pyqrcode,pyzbar.pyzbar as zbar
from PIL import Image
import os,sys,time,base64,gzip,binascii
import json,shutil,os
class app_qr_handler:
    def __init__(self):
        self.defaultQRName=self.mkdefaultName()

    def mkdefaultName(self):
        return '{}-SN:{}-QRCODE.png'.format(time.strftime('%H:%M:%S_%d.%m.%y',time.localtime()),binascii.hexlify(os.urandom(8)).decode())

    def createQrCode(self,data,fname=None,scale=6,version=35,error='H',mode=None,encoding=None,tmpdir=None):
        path=None
        qr=pyqrcode.create(data,version=version,error=error,mode=mode,encoding=encoding)
        if fname == None:
            fname=self.defaultQRName
        if tmpdir == None:
            try:
                path=os.path.join('.',fname)
                qr.png(path,scale=scale)
            except:
                path=os.path.join(os.environ['HOME'],fname)
                qr.png(path,scale=scale)
        else:
            try:
                path=os.path.join(tmpdir,fname)
                qr.png(path,scale=scale)
            except:
                path=os.path.join(os.environ['HOME'],fname)
                qr.png(path,scale=scale)

        self.defaultQRName=path

    def decodeOneQrCode(self,fname):
        return zbar.decode(Image.open(fname))

class reader:
    dataStore={}
    '''
    dataStore={
        'chunk[id]_chunk[pos]':{
            'id':'',
            'pos':'',
            'end':'',
            'dat':'',
        }
    }

    '''
    def __init__(self):
        self.docID=base64.b64encode(os.urandom(8))

    def getls(self,targetName='',directory='./data',mod=8):
        if not os.path.exists(directory):
            exit('{} : does not exist!'.format(directory))
        files=os.listdir(directory)
        targetName+='.'
        files=[i for i in files if i.startswith(targetName)] 
        numsNew=[]
        nums=sorted([int(i.split('.')[-1]) for i in files])
        start=nums[0]
        end=nums[-1]
        for i in nums:
            if len(str(i)) < len(str(nums[-1])):
                i='0'*(len(str(nums[-1]))-len(str(i)))+str(i)
                i='0'*mod+i
            else:
                i='0'*mod+str(i)

            numsNew.append(i)
        nums=[os.path.join(directory,'{}{}'.format(targetName,str(i))) for i in numsNew]  
        for i in [numsNew,files]:
            del(i)
        
        nums=[i for i in nums if os.path.exists(i)]
        if nums == []:
            moddy=0
            for i in os.listdir(directory):
                print(i)
                moddy=(len(i.split('.')[-1])-len(str(int(i.split('.')[-1]))))-1
                
            exit('you might need to adjust your mod number to "{}"'.format(moddy))
        return nums,start,end

    def readChunk(self,fname):
        with open(fname,'rb') as ifile:
            return ifile.read(),fname.split('.')[-1]

    def formatChunkData(self,chunkData,pos,end):
        chunkData=base64.b64encode(chunkData)
        formatted=self.docID+b':'+bytes(str(pos),'utf-8')+b':'+chunkData+b':'+bytes(str(end),'utf-8')
        return formatted

    def mkcodes(self,targetName,chunkDir='./data',tmpdir=None,mod=8,scale=3):
        if tmpdir != None:
            if not os.path.exists(tmpdir):
                os.mkdir(tmpdir)
            else:
                 shutil.rmtree(tmpdir)
                 os.mkdir(tmpdir)
        else:
            #fix later
            tmpdir='.'

        chunkNames=self.getls(targetName=targetName,mod=mod,directory=chunkDir)
        for x in chunkNames[0]:
            chunk=self.readChunk(x)
            form=self.formatChunkData(chunk[0],chunk[1],chunkNames[2])
            a=app_qr_handler()
            a.createQrCode(form,tmpdir=tmpdir,scale=scale)
            print(form)
        
    def readData(self,tmpdir='./qrcodes',resultdir='./result',resultJson='./result.json',useLog=False,ofname='./final.asmb'):
        if useLog == False:
            if not os.path.exists(resultdir):
                try:
                    os.mkdir(resultdir)
                except:
                    print('could not make {}'.format(resultdir))
                    exit()
            for i in os.listdir(tmpdir):
                decode=app_qr_handler()
                chunk=decode.decodeOneQrCode(os.path.join(tmpdir,i))
                self.storeData(self.breakData(chunk))
                print('\033[1;31;40m{0}\033[1;40;m{1}'.format(i,chunk))
            with open(os.path.join(resultdir,resultJson),'w') as log:
                json.dump(self.dataStore,log)
        elif useLog == True:
            with open(os.path.join(resultdir,resultJson),'r') as data:
                self.dataStore=json.load(data)
        self.assemble_2(resultDir=resultdir,ofname=ofname)

    def breakData(self,chunk):
        nchunk={}
        chunk=chunk[0].data.decode().split(':')
        nchunk['id']=chunk[0]
        nchunk['pos']=chunk[1]
        nchunk['dat']=chunk[2]
        nchunk['end']=chunk[3]
        return nchunk

    def storeData(self,chunk,returnChunk=False):
        #data logging
        key='{}_{}'.format(chunk['id'],chunk['pos'])
        self.dataStore[key]={
                'id':chunk['id'],
                'pos':chunk['pos'],
                'end':chunk['end'],
                'dat':chunk['dat'],
        }
        if returnChunk == True:
            return key,self.dataStore
            self.dataStore={}


    def ordered_access(self,accept):
        orders=[]
        keys=[]
        for key in accept.keys():
            if 'pos' in accept[key].keys():
                orders.append(int(accept[key]['pos']))
        orders=sorted(orders)
        for pos in orders:
            for key in accept.keys():
                if int(accept[key]['pos']) == int(pos):
                    keys.append(key)
        return keys

    def assemble_1(self):
        keys=self.ordered_access(self.dataStore) 
        return keys

    def assemble_2(self,resultDir,ofname='final.asmb'):
        keys=self.assemble_1()
        with open(os.path.join(resultDir,ofname),'wb') as ofile:
            for i in keys:
                chunk=base64.b64decode(self.dataStore[i]['dat'].encode())
                ofile.write(chunk)


if __name__ == "__main__":
    f=reader()
    #takes data chunks created from create-chunks.sh and converts them to 
    #qrcodes for application to items passing through a checkpoint
    #please note for even a small file, this SLOW!
    #scale = how big the code will be
    #tmpdir = where the codes will be stored
    #arg1 datachunks prefix
    #chunkDir = where the data chunks to be converted to qrcodes will are stored
    #f.mkcodes('smuggler.tar.xz',tmpdir='./qrcodes',mod=7,scale=2,chunkDir='./data')
    
    ###f.readData() doc########
    #useLog = false will build a dataLog from the data stored in qrcode images in tmpdir
    #useLog = true will use a datalog to recreate the file stored in the qrcodes
    #tmpdir = where qrcodes are stored
    #resultdir =  where logfile and assembled data file are stored
    #resultJson = the logfile
    #ofname = the final assembled datafile stored in resultdir
    # useLog option is in the event that manual assembly of the data log is done
    f.readData(useLog=False,ofname='smuggler.tar.xz',tmpdir='./qrcodes',resultdir='./result',resultJson='result.json')
    
