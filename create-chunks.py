#! /usr/bin/env python3
import os,sys
class sliced:
    def __init__(self):
        pass

    def writeChunk(self,fname,chunk,pos):
        print(pos)

    def dicer(self,fname='data.gen',chunkDir='./data',byteSize=512):
        pos=0
        with open(fname,'rb') as data:
            while True:
                d=data.read(byteSize)
                if not d:
                    break
                self.writeChunk(fname,d,pos)
                pos+=1

if __name__ == "__main__":
    app=sliced()
    app.dicer('smuggler.tar.xz')
