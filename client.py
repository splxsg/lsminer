#!/usr/bin/python3
from tools import *
import time
import socket
import uuid
import json
import os
import logging
import queue
import threading
import sys
import subprocess
import shlex
from datetime import timedelta
from datetime import datetime
import tarfile
import signal
import copy

from string import Template

from gpumon import *
from minerinfo import *

logging.basicConfig(level = logging.INFO, format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt = '%Y-%m-%d  %H:%M:%S %a')

#commond queue
q = queue.Queue(0)

class lsminerClient(object):
    def __init__(self):
        self.cfg = {}
        self.sock = None
        self.minerargs = {}
        self.minerpath = ''
        self.subprocess = None
        self.mthread = None
        self.rthread = None
        self.gthread = None
        self.gcthread = None
        self.minerstatus = 0
        self.startime = datetime.now()
        self.minertime = datetime.now()
        self.accesskey = getAccessKey()
        self.nvcount = nvmlGetGpuCount()
        self.amdcount = fsGetGpuCount()
        self.gpuType = 1 if self.nvcount > self.amdcount else 2    #nvidia==1, amd==2
        self.dog = 0
        self.gpuinfo = None
        self.gpuclock = None
        self.ethPid = ''

    def __del__(self):
        pass

    def getClientUptimeMinutes(self):
        delta = datetime.now() - self.startime
        return delta.seconds // 60

    def getMinerUptimeMinutes(self):
        delta = datetime.now() - self.minertime
        return delta.seconds // 60

    def getGpuInfo(self):
        if self.gpuType == 1:
            return nvmlGetGpuInfo()
        else:
            return fsGetGpuInfo()

    def getGpuClock(self):
        if self.gpuType == 1:
            return nvmlGetGpuClock()
        else:
            return fsGetGpuClock()

    def checkServerConnection(self):
        try:
            cs = self.cfg['ip'].strip() + ':' + str(self.cfg['port'])
            with os.popen('netstat -ent') as p:
                netlines = p.read().splitlines(False)
                for line in netlines:
                    if cs in line and 'ESTABLISHED' in line:
                        return True
        except Exception as e:
            logging.error("function checkServerConnection exception. msg: " + str(e))
            logging.exception(e)
        return False

    def connectSrv(self):
        try:
            logging.info('lsminerClient start connecting server: '+ str(self.cfg['ip'])+':'+ str(self.cfg['port']))
            self.sock = socket.create_connection((self.cfg['ip'], self.cfg['port']), 3)
            self.sock.setblocking(True)
            self.sock.settimeout(70)
        except Exception as e:
            logging.error('connectSrv exception. msg: ' + str(e))
            logging.exception(e)
            time.sleep(3)
            self.sock = None
            #q.put(1)
            
    def GenerateAMDdeviceID(self, gpuinfo):
        gpustatus = ""
        try:
            if gpuinfo:
                mc = len(gpuinfo)
                for i in range(len(gpuinfo)):
                    if i < mc-1:
                        gpustatus += gpuinfo[i]['name'] + '$'
                    else:
                        gpustatus += gpuinfo[i]['name']
        except Exception as e:
            logging.error('generate amd device id error:'+str(e))
        return gpustatus

    def getSystemMemInfo(self):
        try:
            f = open('/proc/meminfo', 'r')
            for line in f:
                if line.startswith('MemTotal:'):
                    mem_total = int(line.split()[1])
                elif line.startswith('MemFree:'):
                    mem_free = int(line.split()[1])
                elif line.startswith('Buffers:'):
                    mem_buffer = int(line.split()[1])
                elif line.startswith('Cached:'):
                    mem_cache = int(line.split()[1])
                elif line.startswith('SwapTotal:'):
                    vmem_total = int(line.split()[1])
                elif line.startswith('SwapFree:'):
                    vmem_free = int(line.split()[1])
                else:
                    continue
            f.close()
        except:
            return None
        return vmem_total/1024, mem_total/1024

    def getSystemDiskInfo(self):
        statvfs = os.statvfs('/')
        total_disk_space = statvfs.f_frsize * statvfs.f_blocks
        free_disk_space = statvfs.f_frsize * statvfs.f_bfree
        return free_disk_space/1024/1024, total_disk_space/1024/1024 
    
    def getSystemInfo(self):
        reqData = {}
        reqData['method'] = 18
        mem_info = self.getSystemMemInfo()
        reqData['vmemory'] = mem_info[0]
        reqData['pmemory'] = mem_info[1]
        disk_info = self.getSystemDiskInfo()
        reqData['free'] = disk_info[0]
        reqData['total'] = disk_info[1]            

        reqjson = json.dumps(reqData)
        reqjson += '\r\n'
        return reqjson

    #client can send system info when user logined in server.
    def sendSYSinfo(self):
        reqjson = self.getSystemInfo()
        logging.info('lsminerClient send system info.')
        logging.info(reqjson)
        self.sock.sendall(reqjson.encode("utf-8"))
        
    def sendLoginReq(self):
        try:
            if self.gpuType == 1:
                cnt = nvmlGetGpuCount()
                name = nvmlGetGpuName()
            else:
                cnt = fsGetGpuCount()
                name = self.GenerateAMDdeviceID(fsGetGpuInfo())
            reqData = {}
            reqData['method'] = 1
            reqData['accesskey'] = self.accesskey

            if self.cfg['wkname']:
                reqData['wkname'] = self.cfg['wkname']
            else:
                reqData['wkname'] = getLanIp()#.replace('.', 'X')

            if self.cfg['wkid']:
                reqData['wkid'] = self.cfg['wkid']
            else:
                reqData['wkid'] = getWkid()

            reqData['devicename'] = name
            reqData['devicecnt'] = cnt
            reqData['appver'] = getClientVersion()
            reqData['platform'] = self.gpuType
            reqData['driverver'] = self.cfg['driverver']
            reqData['os'] = self.cfg['os']
            reqjson = json.dumps(reqData)
            reqjson += '\r\n'
            logging.info('lsminerClient send login request.')
            logging.info(reqjson)
            self.sock.sendall(reqjson.encode("utf-8"))

          #超时 应重启客户端 检查超时原因  
        except Exception as e:
            logging.error('sendLoginReq exception. msg: ' + str(e))
            logging.exception(e)
            time.sleep(1)
            if not self.checkServerConnection():
                #subprocess.run('sudo systemctl restart miner', shell=True)
                self.sock = None
            return None         

    def sendGetMinerArgsReq(self):
        try:
            reqData = {}
            reqData['method'] = 2
            reqData['os'] = self.cfg['os']
            reqjson = json.dumps(reqData)
            reqjson += '\r\n'
            logging.info('lsminerClient send get miner args.')
            logging.info(reqjson)
            self.sock.sendall(reqjson.encode("utf-8"))
        except Exception as e:
            logging.error('sendGetMinerArgsReq exception. msg: ' + str(e))
            logging.exception(e)
            time.sleep(1)
            if not self.checkServerConnection():
                #subprocess.run('sudo systemctl restart miner', shell=True)
                self.sock = None
            return None

    def sendLogoutReq(self):
        try:
            reqData = {}
            reqData['method'] = 6
            reqData['os'] = self.cfg['os']
            reqjson = json.dumps(reqData)
            reqjson += '\r\n'
            logging.info('lsminerClient send logout request.')
            logging.info(reqjson)
            self.sock.sendall(reqjson.encode("utf-8"))
        except Exception as e:
            logging.error('sendLogoutReq exception. msg: ' + str(e))
            logging.exception(e)
            return None

    def onWelcome(self, msg):
        logging.info('recv server connecting msg: ' + str(msg))
        logging.info('connect server ok.')
        q.put(2)
        #thread = threading.Thread(target=lsminerClient.ttyshareProc, args=(self,))
        #thread.start()
        #logging.info('after ttyshareproc')
        self.dog = 0

    def onLoginResp(self, msg):
        logging.info('recv server login msg: ' + str(msg))
        if 'result' in msg and msg['result']:
            logging.info('login ok.')
            self.sendSYSinfo()
            q.put(3)
        else:
            logging.info('login error. msg: ' + msg['error'])
            q.put(6)
            time.sleep(1)
            q.put(1)
    
    def getReportData(self, mcfg):
        try:
            print("==========start getreportdata============")
            reqData = {}
            reqData['method'] = 3
            reqData['minerver'] = mcfg['minerver']
            reqData['uptime'] = self.getMinerUptimeMinutes()
            reqData['minerstatus'] = self.minerstatus
            gpuinfo = self.gpuinfo#getGpuInfo()
            print(gpuinfo)
            gpuclock = self.gpuclock#getGpuClock()
            print(gpuclock)
            if gpuinfo:
                minerinfo = getMinerStatus(mcfg)
                gpustatus = ""                
                if not minerinfo:
                    reqData['hashrate'] = 0
                    for i in range(len(gpuinfo)):
                        gpustatus += str(i) + '|'+ gpuinfo[i]['name'] + '|' + str(gpuinfo[i]['tempC']) + '|0|' + str(gpuinfo[i]['fanpcnt']) + '|' + str(gpuinfo[i]['power_usage']) + '$'
                        
                else:
                    reqData['hashrate'] = minerinfo['totalhashrate']
                    mc = len(minerinfo['hashrate'])
                    j = 0
                    for i in range(len(gpuinfo)):
                        if j < mc:
                            if gpuclock:
                                if gpuclock[i]['currentCoreClock'] == 0:
                                    gpustatus += str(i) + '|'+ gpuinfo[i]['name'] + '|' + str(gpuinfo[i]['tempC']) + '|0|' + str(gpuinfo[i]['fanpcnt']) + '|' + str(gpuinfo[i]['power_usage']) + '$'
                                else:                                    
                                    gpustatus += str(i) + '|'+ gpuinfo[i]['name'] + '|' + str(gpuinfo[i]['tempC']) + '|' + str(minerinfo['hashrate'][j]) + '|' + str(gpuinfo[i]['fanpcnt']) + '|' + str(gpuinfo[i]['power_usage']) + '$'
                                    j = j + 1
                            else:
                                gpustatus += str(i) + '|'+ gpuinfo[i]['name'] + '|' + str(gpuinfo[i]['tempC']) + '|' + str(minerinfo['hashrate'][j]) + '|' + str(gpuinfo[i]['fanpcnt']) + '|' + str(gpuinfo[i]['power_usage']) + '$'
                                j = j + 1
                        else:
                            gpustatus += str(i) + '|'+ gpuinfo[i]['name'] + '|' + str(gpuinfo[i]['tempC']) + '|0|' + str(gpuinfo[i]['fanpcnt']) + '|' + str(gpuinfo[i]['power_usage']) + '$'                            
                gpustatus += str(self.getClientUptimeMinutes())
                reqData['gpustatus'] = gpustatus           
            if gpuclock:
                gpuclockinfo = ""
                for i in range(len(gpuclock)):
                    gpuclockinfo += str(i) + '|' + gpuclock[i]['memmaker'] +'|'+ str(gpuclock[i]['baseCoreClock']) + '|' + str(gpuclock[i]['currentCoreClock']) + '|' + str(gpuclock[i]['baseMemoryClock']) + '|' + str(gpuclock[i]['currentMemoryClock']) + '$'
                reqData['gpuinfo'] = gpuclockinfo
               
            reqData = json.dumps(reqData) + '\r\n'
            print("==========end getreportdata============")
            return reqData
        except Exception as e:
            logging.error("function getReportData exception. msg: " + str(e))
            logging.exception(e)
        return None

    def gpuSTATThread(self):
        while True:
            try:
                time.sleep(float(self.cfg['reportime']))
                logging.info("gpuSTATThread") 
                self.gpuinfo = self.getGpuInfo()
                logging.info("gpuSTATThread done")
            except Exception as e: 
                logging.error("function gpuSTATThread exception. msg: " + str(e))
                time.sleep(1)

    def gpuClockThread(self):
        while True:
            try:
                time.sleep(float(self.cfg['reportime']))
                logging.info("gpuClockThread") 
                self.gpuclock = self.getGpuClock()
                logging.info("gpuClockThread done")
            except Exception as e: 
                logging.error("function gpuClockThread exception. msg: " + str(e))
                time.sleep(1)

    def reportThread(self):
        while True:
            try:                
                time.sleep(float(self.cfg['reportime']))
                if self.dog > 1:
                    logging.error("=========dog server connection exception. restart miner=============")
                    self.dog = 0
                    #os.system('sudo systemctl restart miner')
                #check ttyshare connection
                #if not self.checkTTYServerConnection():
                #    thread = threading.Thread(target=lsminerClient.ttyshareProc, args=(self,))
                #    thread.start()
                if self.sock == None:
                    logging.info('reportThread client socket == None. sleep 1 second.')
                    time.sleep(1)
                    continue
                #mcfg = self.minerargs
                logging.info("before getReportData")
                reqData = self.getReportData(self.minerargs)
                logging.info("after getReportData")
                while not reqData:
                    logging.warning('getReportData failed. sleep 3 seconds and try again.')
                    time.sleep(3)
                    reqData = self.getReportData(self.minerargs)
                logging.info('lsminerClient send miner report data.')
                logging.info(reqData)
                if self.sock:
                    self.sock.sendall(reqData.encode('utf-8'))
                    self.dog += 1
                else:
                    logging.warning('socket unusable.')
                    time.sleep(1)
                    if not self.checkServerConnection():
                        #subprocess.run('sudo systemctl restart miner', shell=True)
                        #q.put(1)
                        self.sock = None
            except Exception as e:
                logging.error("function reportThread exception. msg: " + str(e))
                logging.exception(e)
                time.sleep(1)
                if not self.checkServerConnection():
                    #subprocess.run('sudo systemctl restart miner', shell=True)
                    #q.put(1)
                    self.sock = None

    def getNewMinerFile(self, mcfg):
        try:
            path = './miners/temp.tar.xz'
            while not downloadFile(mcfg['minerurl'], path):
                logging.error("download miner kernel file failed. sleep 3 seconds and try later.")
                time.sleep(3)

            with tarfile.open(path) as tar:
                tar.extractall('./miners')
                #os.remove(path)
                self.minerpath = './miners/' + mcfg['minerver'] + '/' + mcfg['minername']
                return self.minerpath
        except Exception as e:
            logging.error("function getNewMinerFile exception. msg: " + str(e))
            logging.exception(e)

    def checkMinerVer(self, mcfg):
        try:
            mf = './miners/' + mcfg['minerver']
            if os.path.exists(mf):
                self.minerpath = mf + '/' + mcfg['minername']
                return self.minerpath
            else:
                delcmd = 'rm -rf ./miners/' + mcfg['minerver'].split('_')[0] + '_*'
                os.system(delcmd)
        except Exception as e:
            logging.error("function checkMinerVer exception. msg: " + str(e))
            logging.exception(e)
        return None

    def killAllMiners(self, path):
        try:
            cmd = 'ps -x | grep ' + path
            logging.info("kill all "+cmd)
            with os.popen(cmd) as p:
                lines = p.read().splitlines(False)
                for l in lines:
                    p = l.lstrip().split(' ')
                    if 'grep' in p:
                        continue
                    logging.info('kill task pid: ' + p[0])
                    os.kill(int(p[0]), signal.SIGKILL)
        except Exception as e:
            logging.error("function killAllMiners exception. msg: " + str(e))
            logging.exception(e)

    def InjecEth(self):
        try:
            cmd = 'ps -ax | grep -v grep | grep /EthDcrMiner64'
            logging.info("inject ps "+cmd)
            with os.popen(cmd) as p:
                lines = p.read().splitlines(False)
                for l in lines:
                    p = l.lstrip().split(' ')
                    if 'grep' in p:
                        continue
                    if 'python3' in p:
                        continue
                    if 'sudo' in p:
                        continue
                    logging.info('injec pid5: ' + p[0] + ',' + self.ethPid)
                    if self.ethPid != p[0]:
                        self.ethPid = p[0]
                        time.sleep(10)
                        cmd = 'sudo /home/lsminer/lsminer/miners/inj /home/lsminer/lsminer/miners/p1.so ' + p[0]
                        logging.info("inject cmd "+cmd)
                        subprocess.run(cmd, shell=True)

                        #with os.popen(cmd) as pp:
                        #    result = pp.read().splitlines(False)
                        #    logging.info("inject result " + result)
                    break
        except Exception as e:
            logging.error("function InjecEth exception. msg: " + str(e))
            logging.exception(e)
            
    def getMinerProcessCounts(self, minerName):
        try:
            cmd = 'ps -aux | grep -v grep | grep ' + minerName
            print('bbbbbbbbbbbbbbbbbbbbbbbb')
            print(cmd)
            with os.popen(cmd) as p:
                lines = p.read().splitlines(False)
                for l in lines:
                    b = l.lstrip().split(' ')
                    if 'grep' in b:
                        continue
                    if 'python3' in b:
                        continue
                    if 'sudo' in b:
                        continue
                    countn = countn + 1
            return countn         
            #cmd = 'ps -aux | grep -v grep | grep ' + minerName
        except Exception as e:
                logging.error("function getMinerProcessCounts exception. msg: " + str(e))
                logging.exception(e)
                return 0

    def minerThreadProc(self):
        try:
            mcfg = self.minerargs
            if not self.checkMinerVer(mcfg):
                self.getNewMinerFile(mcfg)
                subprocess.run('bash /usr/bin/lsminer_rw', shell=True)
            #run miner kernel by screen 
            arg = self.minerpath + ' ' + mcfg['customize']
            cmdtmp = Template('screen -dm -S minerkernel -t minerkernel -L bash -c "python3 /home/lsminer/lsminer/kernel.py ${arg}"')
            cmd = cmdtmp.substitute(arg=arg)
            subprocess.run(cmd, shell=True)

            self.minerstatus = 1

            #update miner time
            self.minertime = datetime.now()
            while True:
                minerProcount = self.getMinerProcessCounts(self.minerpath[2:])
                logging.info("miner count: "+str(minerProcount))
                if minerProcount == 0:
                    self.minerstatus = 0
                    logging.info('miner terminated. client will be getMinerargs and restart.')
                    q.put(3)
                    break
                else:
                    self.InjecEth()
                    time.sleep(3)
        except Exception as e:
            logging.error("function minerThread exception. msg: " + str(e))
            logging.exception(e)

    def onGetMinerArgs(self, msg):
        try:
            logging.info('recv server get miner args msg: ' + str(msg))
            if 'result' in msg and msg['result']:
                logging.info('get miner args ok.')
                
                
                self.minerargs = msg
                logging.info(self.minerargs)
                #kill miner process, the miner thread will exit
                if self.minerpath:
                    self.killAllMiners(self.minerpath[1:])

                #start new miner thread
                self.mthread = threading.Thread(target=lsminerClient.minerThreadProc, args=(self,))
                self.mthread.start()
                
                #start new report Thread
                if self.rthread == None:
                    self.gpuinfo = self.getGpuInfo()
                    self.gpuclock = self.getGpuClock()
                    self.rthread = threading.Thread(target=lsminerClient.reportThread, args=(self,))
                    self.rthread.start()
                if self.gcthread == None:
                    self.gcthread = threading.Thread(target=lsminerClient.gpuClockThread, args=(self,))
                    self.gcthread.start()
                if self.gthread == None:
                    self.gthread = threading.Thread(target=lsminerClient.gpuSTATThread, args=(self,))
                    self.gthread.start()
            else:
                logging.info('get miner args error. msg: ' + msg['error'])
                q.put(3)
        except Exception as e:
            logging.error("function onGetMinerArgs exception. msg: " + str(e))
            logging.exception(e)

    def onReportResp(self, msg):
        logging.info('recv server report msg: ' + str(msg))
        self.dog -= 1

    def onUpdateMinerArgs(self, msg):
        logging.info('recv server update miner args msg: ' + str(msg))
        q.put(3)

    def onClientUpdate(self, msg):
        logging.info('recv server client update msg: ' + str(msg))
        #kill miner process, exit client.py
        if self.minerpath:
            self.killAllMiners(self.minerpath[1:])
        self.sock.close()
        time.sleep(0.5)
        sys.exit(123)

    def OverClockProc(self,msg):
        logging.info('recv server overclock msg: ' + str(msg))

        cores = ''
        mems = ''
        pows = ''
        temps = ''
        fans = ''

        for odata in msg['params'].split('$'):
            args = odata.split('|')
            cores += args[1] + ','
            mems += args[2] + ','
            pows += args[3] + ','
            temps += args[4] + ','
            fans += args[5] + ','

        os.putenv('GPU_COUNT_NV', '0')
        os.putenv('NV_CORE', '')
        os.putenv('NV_MEMORY', '')
        os.putenv('NV_POWER', '')
        os.putenv('NV_TEMP', '')
        os.putenv('NV_FAN', '')
        os.putenv('GPU_COUNT_AMD', '0')
        os.putenv('AMD_CORE', '')
        os.putenv('AMD_MEMORY', '')
        os.putenv('AMD_POWER', '')
        os.putenv('AMD_TEMP', '')
        os.putenv('AMD_FAN', '')

        if self.gpuType == 1:
            os.putenv('GPU_COUNT_NV', str(self.nvcount))
            os.putenv('NV_CORE', cores)
            os.putenv('NV_MEMORY', mems)
            os.putenv('NV_POWER', pows)
            os.putenv('NV_TEMP', temps)
            os.putenv('NV_FAN', fans)
        else:
            #pass
            os.putenv('GPU_COUNT_AMD', str(self.amdcount))
            os.putenv('AMD_CORE', cores)
            os.putenv('AMD_MEMORY', mems)
            os.putenv('AMD_POWER', pows)
            os.putenv('AMD_TEMP', temps)
            os.putenv('AMD_FAN', fans)
        
        #overclock get over clocl args by environment variables
        #os.system('/home/lsminer/lsminer/overclock')
        
        with os.popen('sudo /home/lsminer/lsminer/overclock') as p:
            netlines = p.read().splitlines(False)
            logging.info(netlines)
        
        #get miner args will restart miner
        #q.put(3)
        #restart miner 
        #os.system('sudo systemctl restart miner')

    def onOverClock(self, msg):
        logging.info('recv server oc: ' + str(msg))
        thread = threading.Thread(target=lsminerClient.OverClockProc, args=(self,msg))
        thread.start()

    def processMsg(self, msg):
        if 'method' in msg:
            if msg['method'] == 1:
                self.onLoginResp(msg)
            elif msg['method'] == 2:
                self.onGetMinerArgs(msg)
            elif msg['method'] == 3:
                self.onReportResp(msg)
            elif msg['method'] == 4:
                self.onUpdateMinerArgs(msg)
            elif msg['method'] == 5:
                pass
            elif msg['method'] == 6:
                pass
            elif msg['method'] == 7:
                pass
            elif msg['method'] == 8:
                pass
            elif msg['method'] == 9:
                self.onWelcome(msg)
            elif msg['method'] == 10:
                self.onOverClock(msg)
            elif msg['method'] ==11:
                pass
            elif msg['method'] == 12:
                pass
            elif msg['method'] == 13:
                pass
            elif msg['method'] == 14:
                logging.info('this method had removed. see lsremote.py')
            elif msg['method'] == 15:
                self.onClientUpdate(msg)
            elif msg['method'] == 16:
                pass
            elif msg['method'] == 18:
                pass
            else:
                logging.info('unknown server msg method! msg: ' + str(msg))
        else:
            logging.info('unknown server msg! msg: ' + str(msg))

    def recvThread(self):
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
                        #print(buffer)
                        msg = json.loads(buffer)
                        self.processMsg(msg)
                    else:
                        logging.warning('lsminerClient recv unknown format data.')
                        logging.warning(buffer)
                    buffer = ''
            except Exception as e:
                logging.info('recvThread exception. msg: ' + str(e))
                logging.exception(e)
                time.sleep(1)
                self.sock = None

    '''cmd list: 1 == connect server, 2 == login server, 3 == get miner config'''
    def processCmd(self, cmd):
        if cmd == 1:
            self.connectSrv()
        elif cmd == 2:
            self.sendLoginReq()
        elif cmd == 3:
            self.sendGetMinerArgsReq()
        elif cmd == 6:
            self.sendLogoutReq()
        elif cmd == 14:
            logging.info('this cmd had removed. see lsremote.py')
        else:
            logging.error('unknown cmd. cmd: ' + str(cmd))

    def init(self):
        self.cfg = loadCfg()
        thread = threading.Thread(target=lsminerClient.recvThread, args=(self,))
        thread.start()
        
    def run(self):
        while True:
            try:
                cmd = q.get()
                self.processCmd(cmd)
            except Exception as e:
                logging.info("main loop run exception. msg: " + str(e))
                logging.exception(e)
                logging.info("sleep 3 seconds and retry...")
                time.sleep(3)

if __name__ == '__main__':
    client = lsminerClient()
    client.init()
    client.run()
