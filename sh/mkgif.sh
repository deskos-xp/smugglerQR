#! /usr/bin/env bash
python3 lib/mkStartEnd.py
#this will be replaced with a python util later
convert -delay 500 START.png `ls -t1 qrcodes | sed s/^/'qrcodes\//g'` END.png data.gif
rm END.png START.png
