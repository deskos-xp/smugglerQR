claptrap encryption tool -- use to encrypt data chunks before placing them on qrcodes
lib/smuggler.py -- convert data chunks to/from qrcodes
lib/chunkless.py -- take data file, and convert to datafiles of chunk size byteSize for lib/smuggler.py to digest
lib/handle_one.py -- get data from one qrcode and create/append to logfile
sh/create-chunks.sh -- take data file and make chunked data for smuggler.py [deprecated,smuggler.py now includes this functionality]
sh/mkgif.sh -- take qrcodes and convert to a animated qr gif
lib/mkStartEnd.py -- makes indicative START and END images for mkgif.sh
lib/mkgif.py -- make a gif from files provided by smuggler.py
smuggler.py -- cmdline utility that controls operations
lib/camcorder.py -- capture barcodes from webcam
