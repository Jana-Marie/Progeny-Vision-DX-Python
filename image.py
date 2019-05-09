#!/bin/python3.7
import sys
import struct
from PIL import Image

sizeX = 1640
sizeY = 1262

inData = open(sys.argv[1],'rb')
data = inData.read();

fmt = '>' + str(sizeX*sizeY) + 'H'  # > BIG ENDIAN    < LITTLE ENDIAN
pix = struct.unpack(fmt, data)
lightest = max(pix)
scaled = ''.join(chr(int((float(p) / lightest)**(1/2.2) * 255)) for p in pix)
im = Image.frombytes('L', (sizeX,sizeY), scaled.encode(), 'raw')
im.show()
