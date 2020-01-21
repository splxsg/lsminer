#!/usr/bin/python3
from tools import *
import os
import sys
import time
from urllib import request
from urllib import parse
import subprocess
import tarfile
import hashlib

import logging

logging.basicConfig(level = logging.INFO, format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt = '%Y-%m-%d  %H:%M:%S %a')

headers = {
    'Accept':'*/*',
    'Accept-Encoding':'gzip, deflate',
    'Accept-Language':'zh-CN,zh;q=0.8',
    'Connection':'keep-alive',
    'Cache-Control': 'no-cache',
    'Content-Type':'application/x-www-form-urlencoded',
    'User-Agent':'lsminer client for linux'
    }


def checkClientUpdate(ver, url):
    ''' return true = client has been updated or false = client has not been updated.'''
    try:
        logging.info("in checkclientupdate")
        body = {}
        body['version'] = ver
        logging.info('update.py current version: ' + str(body))
        data = parse.urlencode(body).encode('utf-8')
        req = request.Request(url, headers=headers, data=data)
        with request.urlopen(req) as f:
            resdict = json.loads(f.read().decode('utf-8'))
            logging.info('update.py get update json msg: ' + str(resdict))

        if resdict['result']:
            filepath = '/home/lsminer/lsminer/' + resdict['appname']
            while True:
                if downloadFile(resdict['appurl'], filepath):
                    logging.info(getFileMd5(filepath))
                    logging.info(resdict['appmd5'])
                    if getFileMd5(filepath) == resdict['appmd5']:
                        logging.info('file download ok.')
                        with tarfile.open(filepath) as tar:
                            tar.extractall('/home/lsminer/lsminer/')
                        subprocess.run('sudo /usr/bin/lsminer_rw', shell=True)
                        return True
                    else:
                        logging.warning("lsminer client package md5 hash wrong. sleep 3 seconds and try later.")
                else:
                    logging.warning("lsminer client download lsminer client package file failed. sleep 3 seconds and try later.")
                time.sleep(3) 
        else:
            logging.error(resdict['error'])

    except Exception as e:
        logging.error("function reportThread exception. msg: " + str(e))
        logging.exception(e)
    return False

if __name__ == '__main__':
    try:
        logging.info("in update.py")
        updateurl = 'http://lsminer.yunjisuan001.com:23335/appupdate_linux'
        appver = getClientVersion()
        logging.info("gotversion")
        while True:
            if checkClientUpdate(appver, updateurl):
                logging.info('client has been updated. lsminer client will restart later.')
                subprocess.run('sudo systemctl restart miner', shell=True)
            if not os.path.exists('/etc/systemd/system/lsremote.service'):            
                subprocess.run('sudo -H /home/lsminer/lsminer/install.sh', shell=True)
                subprocess.run('sudo systemctl restart lsremote', shell=True)
            process = subprocess.run('python3 /home/lsminer/lsminer/client.py', shell=True)
            if process.returncode == 123:
                logging.info('client recv update msg.')
            else:
                logging.warning('client exit! sleep 3 seconds and try start again.')
                time.sleep(3)

    except Exception as e:
        logging.error('update.py function __main__ exception. msg: ' + str(e))
        logging.exception(e)
    
