#!/usr/bin/python3

import subprocess
import sys
import queue
import time

q = queue.Queue(0)

def run(argv):
    cmd ='sudo ' + ' '.join(argv[1:])
    print('miner run args.\n' + cmd)
    process = subprocess.Popen(cmd, shell=True)
    #pidint = int(process.pid) + 2
    #inj p1.so pidint
    time.sleep(3)
    process.terminate()

if __name__ == '__main__':
    run(sys.argv)
    while True:
        q.get()