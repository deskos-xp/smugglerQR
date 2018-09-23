#! /usr/bin/env bash
split --bytes 256 --numeric-suffixes=0 --suffix-length=11 "$1" data/data.png.
