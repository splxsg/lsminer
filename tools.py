from urllib import request
import time
import socket
import uuid
import json
import os
import hashlib
import gpumon
import logging

logging.basicConfig(level = logging.INFO, format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt = '%Y-%m-%d  %H:%M:%S %a')

defaultConfig = {
    "ip": "47.99.207.149",
    "port": 22457,
    "wkid":"",
    "wkname":"",
    "driverver":"230",
    "os":2,
    "reportime":30
}

def getMac():
    '''获取系统网卡MAC地址'''
    macnum = hex(uuid.getnode())[2:]
    mac = "-".join(macnum[i: i+2] for i in range(0, len(macnum), 2))
    return mac

def getName():
    '''获取电脑名称'''
    return socket.gethostname()

def getIp():
    '''获取系统内网IP地址'''
    return socket.gethostbyname(getName())

def getLanIp():
    with os.popen("ifconfig | sed -En 's/127.0.0.1//;s/.*inet (addr:)?(([0-9]*\.){3}[0-9]*).*/\\2/p'") as p:
        lanIp = p.read().strip()
        return lanIp

def getAccessKey():
    '''获取用户Accesskey'''
    try:
        with open("/home/lsminer/lsminer.conf", "r", encoding="utf-8") as fs:
            key = fs.readline().replace("\n","")
            return key
    except Exception as e:
        logging.error("function getAccessKey exception. msg: " + str(e))
        logging.exception(e)
    return 0

def getClientVersion():
    '''获取客户端版本号'''
    try:
        with open("/home/lsminer/lsminer/version", "r", encoding="utf-8") as fs:
            ver = fs.readline()
            if not ver:
                ver = 100
            return int(ver)
    except Exception as e:
        logging.error("function getClientVersion exception. msg: " + str(e))
        logging.exception(e)
    return 0

def loadCfg():
    '''加载当前目录下的配置文件config.json'''
    userCfg = {}
    cfg = defaultConfig
    try:
        with open("./config.json", "r", encoding="utf-8") as fs:
            userCfg = json.load(fs)
    except Exception as e:
        logging.error("function loadCfg exception. msg: " + str(e))
        logging.exception(e)
    
    cfg.update(userCfg)

    return cfg
    

def saveCfg(cfgdict):
    '''保存当前目录下的配置文件config.json'''
    try:
        with open("./config.json", "w", encoding="utf-8") as fs:
            json.dump(cfgdict, fs)
            return 1
    except Exception as e:
        logging.error("function saveCfg exception. msg: " + str(e))
        logging.exception(e)
    return 0
    
def md5(data):
    '''MD5哈希函数'''
    return str(hashlib.md5(data.encode('utf-8')).hexdigest())

def getFileMd5(file_path):
    """get file md5"""
    try:
        with open(file_path, 'rb') as f:
            md5obj = hashlib.md5()
            md5obj.update(f.read())
            _hash = md5obj.hexdigest()
            return str(_hash).lower()
    except Exception as e:
        logging.error("function getFileMd5 exception. msg: " + str(e))
        logging.exception(e)
    return ''


def getWkid():
    '''获取Wkid(网卡MAC字符串MD5哈希值)'''
    return md5('linux-' + getMac() + '-' + getAccessKey())

def getReboot(url):
    '''检测是否需要重启系统'''
    try:
        logging.info("checking reboot")
        req = request.Request(url)
        with request.urlopen(req) as f:
            return int(f.read().decode('utf-8'))
    except Exception as e:
        logging.error("function getReboot exception. msg: " + str(e))
        logging.exception(e)
    return 0

def getNvidiaCount():
    '''获取NVIDIA显卡的数量'''
    count = 0
    with  os.popen('lspci') as p:
        pci =p.read().splitlines(False)
        for l in pci:
            if 'VGA' in l or '3D controller' in l:
                if 'NVIDIA' in l and 'nForce' not in l:
                    count += 1
    return count

def getAMDCount():
    '''获取AMD显卡的数量'''
    count = 0
    with os.popen('lspci') as p:
        pci = p.read().splitlines(False)
        for l in pci:
            if 'VGA' in l or '3D controller' in l:
                if 'Advanced Micro Devices' in l and 'RS880' not in l:
                    count += 1
    return count

def getVedioCard():
    '''获取显卡列表'''
    cardstr = ""
    with os.popen('lspci') as p:
        pci = p.read().splitlines(False)
        for l in pci:
            if 'VGA' in l or '3D controller' in l:
                name = l.split(': ')[1].strip()
                if cardstr:
                    cardstr = cardstr + "|" + name
                else:
                    cardstr = name
    return cardstr
    
def downloadFile(url, path):
    '''从url下载文件保存到path路径，path包含文件名'''
    try:
        req = request.Request(url)
        with request.urlopen(req) as f:
            with open(path, "wb") as p:
                p.write(f.read())
                p.flush()
                return 1
    except Exception as e:
        logging.error("function downloadFile exception. msg: " + str(e))
        logging.exception(e)
    return 0

if __name__ == '__main__':
    pass
