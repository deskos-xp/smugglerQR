#! /usr/bin/env python3
import os,sys,shutil
class sliced:
    suffix_len=10
    def __init__(self):
        pass

    def maxfiles(self,fname,byteSize=512):
        return int(os.stat(fname().st_size/512))

    def writeChunk(self,fname,chunkDir,chunk,pos):
        #files=selfself.maxfiles(fname)
        suffix=(self.suffix_len-len(str(pos)))*'0'+str(pos)
        name=os.path.join(chunkDir,fname+'.{}'.format(suffix))
        print('"{}" -> "{}"'.format(fname,name))
        with open(name,'wb') as ifile:
            ifile.write(chunk)

    def mkChunkDir(self,chunkDir='./data'):
        if not os.path.exists(chunkDir):
            try:
                os.mkdir(chunkDir)
            except:
                print(sys.exc_info())
                exit()
        else:
            shutil.rmtree(chunkDir)
            os.mkdir(chunkDir)

    def dicer(self,fname='data.gen',chunkDir='./data',byteSize=512):
        self.mkChunkDir(chunkDir)
        pos=0
        with open(fname,'rb') as data:
            while True:
                d=data.read(byteSize)
                if not d:
                    break
                self.writeChunk(fname,chunkDir,d,pos)
                pos+=1

if __name__ == "__main__":
    app=sliced()
    app.dicer('smuggler.tar.xz',chunkDir='./data',byteSize=512)
