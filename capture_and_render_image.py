#!/bin/python2.7
import sys
from PIL import Image
import numpy as np
from skimage import io

import matplotlib
import matplotlib.pyplot as plt

from skimage import data, img_as_float
from skimage import exposure

import socket
from threading import Thread
import threading
import signal
import time
import sys

outfile = open(sys.argv[1], 'w')

sizeX = 1262
sizeY = 1640

sensorIP = "192.168.68.64"
hostIP   = "192.168.68.1"

def plot_img_and_hist(image, axes, bins=256):
    # Plot an image along with its histogram and cumulative histogram.

    image = img_as_float(image)
    ax_img, ax_hist = axes
    ax_cdf = ax_hist.twinx()

    # Display image
    ax_img.imshow(image, cmap=plt.cm.gray)
    ax_img.set_axis_off()

    # Display histogram
    ax_hist.hist(image.ravel(), bins=bins, histtype='step', color='black')
    ax_hist.ticklabel_format(axis='y', style='scientific', scilimits=(0, 0))
    ax_hist.set_xlabel('Pixel intensity')
    ax_hist.set_xlim(0, 1)
    ax_hist.set_yticks([])

    # Display cumulative distribution
    img_cdf, bins = exposure.cumulative_distribution(image, bins)
    ax_cdf.plot(bins, img_cdf, 'r')
    ax_cdf.set_yticks([])

    return ax_img, ax_hist, ax_cdf

# thread fuction
def receive(recv):
    c, addr = recv.accept()
    data = ""
    while True:
        # data received from client
        #print("Received:")
        _data = c.recv(2048)
        data += _data

        print '\r>> You have finished %d' % len(data),
        sys.stdout.flush()
        #print(len(data))
        if len(_data) == 0:
            outLen = len(data)-4139360
            print(str(len(data)) + " Byte Received")
            outfile.write(data[outLen:])
            outfile.close()
            print("exit")
            c.shutdown(socket.SHUT_WR)
            c.close()
            recv.shutdown(socket.SHUT_WR)
            recv.close()
            # send close command
            cmd2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            cmd2.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            cmd2.bind(('0.0.0.0',50452))
            cmd2.connect((sensorIP, port))
            cmd2.sendall(b"ID=000094DA367B\x0d\x0aIP="+hostIP+b"\x0d\x0aPORT=50444\x0d\x0aCMD=CLOSE\x0d\x0a")
            cmd2.shutdown(socket.SHUT_WR)
            cmd2.close()
            return

port = 104                   # The same port as used by the server
cmd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
cmd.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
cmd.bind(('0.0.0.0',50452))

port = 104
recv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
recv.bind(('0.0.0.0',50444))
recv.listen(5)

otterThread = Thread(target=receive, args=(recv, ))
otterThread.start()

def run_program():
        #while True:
        print("Sending...")
        cmd.connect((sensorIP, port))
        #cmd.send(b"ID=000094DA367B\x0d\x0aIP=192.168.68.1\x0d\x0aPORT=50444\x0d\x0aCMD=STATUS\x0d\x0a")
        cmd.sendall(b"ID=000094DA367B\x0d\x0aIP="+hostIP+b"\x0d\x0aPORT=50444\x0d\x0aCMD=CAPTURE\x0d\x0aMODE=4\x0d\x0a")
        #cmd.sendall(b"ID=000094DA367B\x0d\x0aIP=192.168.68.1\x0d\x0aPORT=50444\x0d\x0aCMD=CLOSE\x0d\x0a")
        cmd.shutdown(socket.SHUT_WR)
        cmd.close()
        print("Done.")
        otterThread.join()

        #cmd.shutdown(socket.SHUT_WR)
        #cmd.close()
    #s.sendall(b"ID=000094DA367B\x0d\x0aIP=192.168.68.1\x0d\x0aPORT=50444\x0d\x0aCMD=CAPTURE\x0d\x0aMODE=0\x0d\x0a")
    #data = s.recv(1024)

    #print('Received', repr(data))
def exit_gracefully(signum, frame):
    # restore the original signal handler as otherwise evil things will happen
    # in raw_input when CTRL+C is pressed, and our signal handler is not re-entrant
    global cmd
    global recv
    cmd.close()
    recv.close()
    cmd2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cmd2.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    cmd2.bind(('0.0.0.0',50452))
    cmd2.connect((sensorIP, port))
    cmd2.sendall(b"ID=000094DA367B\x0d\x0aIP="+hostIP+b"\x0d\x0aPORT=50444\x0d\x0aCMD=CLOSE\x0d\x0a")
    cmd2.shutdown(socket.SHUT_WR)
    cmd2.close()
    print("bye.")

    signal.signal(signal.SIGINT, original_sigint)
    sys.exit(1)

    # restore the exit gracefully handler here
    signal.signal(signal.SIGINT, exit_gracefully)

original_sigint = signal.getsignal(signal.SIGINT)
signal.signal(signal.SIGINT, exit_gracefully)
run_program()



print ("\nReading: "+sys.argv[1])
img = np.fromfile(sys.argv[1], dtype=">u2")
img = np.reshape(img, (sizeY, sizeX))
#image = image / (2  6)
img = (2 ** 16) - img
img = img -1
lx, ly = img.shape
img = img[100:lx , 13 : ly ]

image = Image.fromarray(np.uint32(img), 'I')
#image.show()
timestr = time.strftime("%Y%m%d-%H%M%S")
image.save('pictures/' + timestr + '.png')

# Contrast stretching
p2, p98 = np.percentile(img, (2, 98))
img_rescale = exposure.rescale_intensity(img, in_range=(p2, p98))

# Equalization
img_eq = exposure.equalize_hist(img)

# Adaptive Equalization
img_adapteq = exposure.equalize_adapthist(img, clip_limit=0.03)

# Display results
fig = plt.figure(figsize=(8, 5))
axes = np.zeros((2, 4), dtype=np.object)
axes[0, 0] = fig.add_subplot(2, 4, 1)
for i in range(1, 4):
    axes[0, i] = fig.add_subplot(2, 4, 1+i, sharex=axes[0,0], sharey=axes[0,0])
for i in range(0, 4):
    axes[1, i] = fig.add_subplot(2, 4, 5+i)

ax_img, ax_hist, ax_cdf = plot_img_and_hist(img, axes[:, 0])
ax_img.set_title('Low contrast image')

y_min, y_max = ax_hist.get_ylim()
ax_hist.set_ylabel('Number of pixels')
ax_hist.set_yticks(np.linspace(0, y_max, 5))

ax_img, ax_hist, ax_cdf = plot_img_and_hist(img_rescale, axes[:, 1])
ax_img.set_title('Contrast stretching')
io.imsave('img_stretched.png', img_rescale)

ax_img, ax_hist, ax_cdf = plot_img_and_hist(img_eq, axes[:, 2])
ax_img.set_title('Histogram equalization')
io.imsave('img_equalized.png', img_rescale)

ax_img, ax_hist, ax_cdf = plot_img_and_hist(img_adapteq, axes[:, 3])
ax_img.set_title('Adaptive equalization')

ax_cdf.set_ylabel('Fraction of total intensity')
ax_cdf.set_yticks(np.linspace(0, 1, 5))

# prevent overlap of y-axis labels
fig.tight_layout()
plt.show()
