#!/usr/bin/python3
from tools import *
import time
import socket
import json
import os
import logging
import queue
import threading
import sys
import subprocess

from string import Template

from gpumon import *
from minerinfo import *

logging.basicConfig(level = logging.INFO, format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt = '%Y-%m-%d  %H:%M:%S %a')

#commond queue
q = queue.Queue(0)

class lsremote(object):
    def __init__(self):
        self.cfg = {}
        self.sock = None
        self.remoteip = None
        self.remoteport = None
        self.ttyserver = self.getTTYServerString()
        self.ttyservicestarting = 0
        self.ttyshareUrl = ''

    def __del__(self):
        pass

    def redlineThreadProc(self):
        while True:
            try:
                url = 'http://api.lsminer.com:37124/redline/' + getWkid()
                reboot = getReboot(url)
                if reboot:
                    logging.warning('recv reboot cmd! system will be reboot.')
                    os.system("sudo reboot")
                else:
                    print('sleep 60 seconds. and check reboot cmd.')
                    time.sleep(60)
            except Exception as e:
                logging.error("redline main loop run exception. msg: " + str(e))
                logging.error("sleep 3 seconds and retry.")
                logging.exception(e)
                time.sleep(3)

    def mainThreadProc(self):
        try:
            while True:
                time.sleep(50)
                reqdata='1\r\n'
                if self.socket and self.logined:
                    self.sock.sendall(reqdata.encode("utf-8"))
                    logging.info('lsremote send online message request.')
        except Exception as e:
            logging.error("lsremote function mainThreadProc exception. msg: " + str(e))
            logging.exception(e)

    def gpuErrorCheckThreadProc(self):
        while True:
            try:
                with open("/var/log/syslog", "r", encoding="utf-8") as fs:
                    text = fs.readline()
                    if text and 'amdgpu' in text and 'VM_CONTEXT1_PROTECTION_FAULT_ADDR' in text;
                        q.put({'cmd': 21, 'msg': '1'})
                        logging.info('found amdgpu error msg in syslog file. system will be reboot later.')
                        time.sleep(3)#wait, be sure reboot msg had sent to server
                        subprocess.run('sudo reboot')
            except Exception as e:
                logging.error("gpu error check thread proc loop run exception. msg: " + str(e))
                logging.error("sleep 3 seconds and retry.")
                logging.exception(e)
                time.sleep(3)

    def init(self):
        self.cfg = loadCfg()
        rthread = threading.Thread(target=lsremote.recvThreadProc, args=(self,))
        rthread.start()
        redthread = threading.Thread(target=lsremote.redlineThreadProc, args=(self,))
        redthread.start()

    def checkTTYServerConnection(self):
        try:
            if self.ttyserver:
                with os.popen('netstat -ent') as p:
                    netlines = p.read().splitlines(False)
                    for line in netlines:
                        if self.ttyserver in line and 'ESTABLISHED' in line:
                            return True
        except Exception as e:
            logging.error("function checkTTYServerConnection exception. msg: " + str(e))
            logging.exception(e)
        return False

    def getTTYServerString(self):
        try:
            with open('./boot/ttyshare', 'r', encoding="utf-8") as text:
                for line in text.readlines():
                    if '--server ' in line:
                        ttyserver = line.split('--server ')[1].strip()
                        logging.info('find tty server string: ' + ttyserver)
                        return ttyserver
            logging.warning('do not find tty server string.')
        except Exception as e:
            logging.error("function getTTYServerString exception. msg: " + str(e))
            logging.exception(e)
        return ''

    def ttyshareProc(self):
        filepath = "/home/lsminer/ttyshare.id"

        #check ttyshare server connection ok? ok = True,
        if not self.checkTTYServerConnection():
            subprocess.run('sudo systemctl stop ttyshare', shell=True)
            time.sleep(1)
            subprocess.run('sudo systemctl start ttyshare', shell=True)

        if not self.ttyservicestarting:
            self.ttyservicestarting = 1
            while True:
                try:
                    if not os.path.exists(filepath):
                        logging.warning('can not find ttyshare.id file. sleep 10 seconds and try again.')
                        time.sleep(10)
                        continue
                    time.sleep(2)
                    with open(filepath, "r", encoding="utf-8") as fs:
                        self.ttyshareUrl = fs.readline().replace("\n","")
                        logging.info("ttyshareurl: " + str(self.ttyshareUrl))
                    q.put({'cmd':14, 'msg':self.ttyshareUrl})#send ttyshare url to server
                    break
                except Exception as e:
                    logging.info('ttyshareProc exception. msg: ' + str(e))
                    logging.exception(e)
                    time.sleep(10)
            self.ttyservicestarting = 0

    def onLoginResp(self, msg):
        logging.info('recv server login msg: ' + str(msg))
        if 'result' in msg and msg['result']:
            mthread = threading.Thread(target=lsremote.mainThreadProc, args=(self,))
            mthread.start()
            gputhread = threading.Thread(target=lsremote.gpuErrorCheckThreadProc, args=(self,))
            gputhread.start()
            thread = threading.Thread(target=lsremote.ttyshareProc, args=(self,))
            thread.start()
            logging.info('lsremote login ok.')
        else:
            logging.info('lsremote login error. msg: ' + msg['error'])
            time.sleep(1)

    def onGetTTYShareId(self, msg):
        logging.info('lsremote recv server get ttyshare msg: ' + str(msg))
        thread = threading.Thread(target=lsremote.ttyshareProc, args=(self,))
        thread.start()

    def onStartMiner(self):
        logging.info('lsremote recv server start miner msg: ' + str(msg))
        subprocess.run('sudo systemctl start miner', shell=True)
    
    def onStopMiner(self):
        logging.info('lsremote recv server stop miner msg: ' + str(msg))
        subprocess.run('sudo systemctl stop miner', shell=True)
    
    def onExceptions(self):
        logging.info('lsremote recv server exception msg: ' + str(msg))

    def processMsg(self, msg):
        if 'method' in msg:
            if msg['method'] == 1:
                self.onLoginResp(msg)
            elif msg['method'] == 14:
                self.onGetTTYShareId(msg)
            elif msg['method'] == 19:
                self.onStopMiner(msg)
            elif msg['method'] == 20:
                self.onStartMiner(msg)
            elif msg['method'] == 21:
                self.onExceptions(msg)
            else:
                logging.info('unknown server msg method! msg: ' + str(msg))
        else:
            logging.info('unknown server msg! msg: ' + str(msg))

    def recvThreadProc(self):
        while True:
            try:
                buffer = ''
                if self.sock == None:
                    logging.info('client socket == None. sleep 1 second.')
                    time.sleep(1)
                    if not self.checkServerConnection():
                        self.connectSrv()
                    continue

                data = self.sock.recv(4096)
                if not data:
                    logging.warning('server close socket. try to reconnect.')
                    time.sleep(1)
                    if not self.checkServerConnection():
                        self.sock = None
                    continue

                buffer += data.decode()
                if '\n' in buffer:
                    if '{' == buffer[0] and '}' == buffer[len(buffer)-2]:
                        msg = json.loads(buffer)
                        self.processMsg(msg)
                    else:
                        logging.warning('lsremote recv unknown format data.')
                        logging.warning(buffer)
                    buffer = ''
            except Exception as e:
                logging.info('recvThreadProc exception. msg: ' + str(e))
                logging.exception(e)
                time.sleep(1)
                self.sock = None

    def checkServerConnection(self):
        try:
            cs = self.remoteip.strip() + ':' + str(self.remoteport)
            with os.popen('netstat -ent') as p:
                netlines = p.read().splitlines(False)
                for line in netlines:
                    if cs in line and 'ESTABLISHED' in line:
                        return True
        except Exception as e:
            logging.error("lsremote function checkServerConnection exception. msg: " + str(e))
            logging.exception(e)
        return False

    def connectSrv(self):
        try:
            logging.info('lsminerClient start connecting server: '+ str(self.cfg['lsremoteaddr'])+':'+ str(self.cfg['lsremoteport']))
            self.sock = socket.create_connection((self.cfg['lsremoteaddr'], self.cfg['lsremoteport']), 3)
            self.sock.setblocking(True)
            self.sock.settimeout(70)
            if self.sock:
                peer = self.sock.getpeername()
                self.remoteip = peer[0]
                self.remoteport = peer[1]
                q.put({'cmd': 2, 'msg': ''})    #send login server cmd
        except Exception as e:
            logging.error('lsremote connectSrv exception. msg: ' + str(e))
            logging.exception(e)
            time.sleep(3)
            self.sock = None

    def sendLoginReq(self):
        try:
            reqData = {}
            reqData['method'] = 1

            if self.cfg['wkid']:
                reqData['wkid'] = self.cfg['wkid']
            else:
                reqData['wkid'] = getWkid()

            reqData['appver'] = getClientVersion()
            reqData['os'] = self.cfg['os']
            reqjson = json.dumps(reqData)
            reqjson += '\r\n'
            logging.info('lsremote send login request.')
            logging.info(reqjson)
            self.sock.sendall(reqjson.encode("utf-8"))
        except Exception as e:
            logging.error('lsremote sendLoginReq exception. msg: ' + str(e))
            logging.exception(e)
            time.sleep(1)
            if not self.checkServerConnection():
                #subprocess.run('sudo systemctl restart lsremote', shell=True)
                self.sock = None
            return None

    def sendTTYShareUrl(self):
        try:
            reqData = {}
            reqData['method'] = 14
            reqData['params'] = self.ttyshareUrl
            reqData['os'] = self.cfg['os']
            reqjson = json.dumps(reqData)
            reqjson += '\r\n'
            logging.info('lsremote send ttyshare url request.')
            logging.info(reqjson)
            self.sock.sendall(reqjson.encode("utf-8"))
        except Exception as e:
            logging.error('lsremote sendTTYShareUrl exception. msg: ' + str(e))
            logging.exception(e)
            time.sleep(1)
            if not self.checkServerConnection():
                self.sock = None
            return None

    def sendException(self, errcode):
        try:
            reqData = {}
            reqData['method'] = 21
            reqData['code'] = errcode
            reqData['os'] = self.cfg['os']
            reqjson = json.dumps(reqData)
            reqjson += '\r\n'
            logging.info('lsremote send exception.')
            logging.info(reqjson)
            self.sock.sendall(reqjson.encode("utf-8"))
        except Exception as e:
            logging.error('lsremote sendTTYShareUrl exception. msg: ' + str(e))
            logging.exception(e)
            time.sleep(1)
            if not self.checkServerConnection():
                self.sock = None
            return None

    '''cmd list: 1 == connect server, 2 == login server'''
    def processCmdMsg(self, cmdmsg):
        logging.info('recv cmd msg. cmdmsg: ' + str(cmdmsg))
        cmd = cmdmsg['cmd']
        msg = cmdmsg['msg']
        if cmd == 1:
            self.connectSrv()
        elif cmd == 2:
            self.sendLoginReq()
        elif cmd == 3:
            pass
        elif cmd == 21:
            self.sendException(int(msg))
        elif cmd == 14:
            self.sendTTYShareUrl()
        else:
            logging.error('unknown cmd. cmd: ' + str(cmd))

    def run(self):
        while True:
            try:
                cmdmsg = q.get()
                self.processmsgMsg(cmdmsg)
            except Exception as e:
                logging.info("main loop run exception. msg: " + str(e))
                logging.exception(e)
                logging.info("sleep 3 seconds and retry...")
                time.sleep(3)

if __name__ == '__main__':
    client = lsminerClient()
    client.init()
    client.run()