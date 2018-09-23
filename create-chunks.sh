#! /usr/bin/env bash
if test -e "./data" ; then
	rm -rf ./data
	mkdir ./data
else
	mkdir ./data
fi
split --bytes 512 --numeric-suffixes=0 --suffix-length=11 "$1" data/data.png.
