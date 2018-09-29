#! /usr/bin/env python3

import os,sys,imageio

class mkgif:
    def __init__(self):
        pass

    def mkgif(self,fnames,fname,duration=5):
        images=[]
        for name in fnames:
            images.append(imageio.imread(name))
            print(' "{}": read'.format(name))
        imageio.mimsave(fname,images,duration=duration,loop=0)
        print("{} : Done!".format(fname))
