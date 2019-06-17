#!/bin/python2.7
import socket
# import thread module
#from thread import *
from threading import Thread
import threading
import signal
import time
import sys

outfile = open(sys.argv[1], 'w')
hostIP = b"192.168.68.1"
sensorIP = "192.168.68.64"

#print_lock = threading.Lock()

#isFinished = 0;
data = ""

# thread fuction
def receive(recv):
    c, addr = recv.accept()
    while True:
        # data received from client
        #print("Received:")
        _data = c.recv(2048)
        data += _data
        #print(len(data))
        if len(_data) == 0:
            outLen = len(data)-4139360
            print(str(len(data)) + " Byte Received")
            outfile.write(data)
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
            cmd2.connect((host, port))
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
        cmd.sendall(b"ID=000094DA367B\x0d\x0aIP="+hostIP+b"\x0d\x0aPORT=50444\x0d\x0aCMD=CAPTURE\x0d\x0aMODE=0\x0d\x0a")
        #cmd.sendall(b"ID=000094DA367B\x0d\x0aIP=192.168.68.1\x0d\x0aPORT=50444\x0d\x0aCMD=CLOSE\x0d\x0a")
        cmd.shutdown(socket.SHUT_WR)
        cmd.close()
        otterThread.join()


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
    cmd2.connect((host, port))
    cmd2.sendall(b"ID=000094DA367B\x0d\x0aIP="+hostIP+b"\x0d\x0aPORT=50444\x0d\x0aCMD=CLOSE\x0d\x0a")
    cmd2.shutdown(socket.SHUT_WR)
    cmd2.close()
    print("bye.")

    outfile.write(data)
    outfile.close()
    signal.signal(signal.SIGINT, original_sigint)
    sys.exit(1)

    # restore the exit gracefully handler here
    signal.signal(signal.SIGINT, exit_gracefully)

original_sigint = signal.getsignal(signal.SIGINT)
signal.signal(signal.SIGINT, exit_gracefully)
run_program()
