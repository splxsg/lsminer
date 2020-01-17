from urllib import request
import time
import socket
import uuid
import json
import os
import logging
from urllib.parse import urlparse

logging.basicConfig(level = logging.INFO, format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt = '%Y-%m-%d  %H:%M:%S %a')

def getMinerStatus_trex(msdict):
	try:
		minerstatus = {}
		minerstatus['uptime'] = msdict['uptime']
		minerstatus['hashrate'] = []
		minerstatus['totalhashrate'] = 0.0
		for device in msdict['gpus']:
			minerstatus['hashrate'].append(device['hashrate'])
			minerstatus['totalhashrate'] += float(device['hashrate'])
		return minerstatus
	except Exception as e:
		logging.error("function getMinerStatus_trex exception. msg: " + str(e))
		logging.exception(e)
	return None

def getMinerStatus_nbminer(msdict):
	try:
		minerstatus = {}
		minerstatus['uptime'] = 0
		minerstatus['hashrate'] = []
		minerstatus['totalhashrate'] = 0.0
		for device in msdict['miner']['devices']:
			minerstatus['hashrate'].append(device['hashrate_raw'])
			minerstatus['totalhashrate'] += float(device['hashrate_raw'])
		return minerstatus
	except Exception as e:
		logging.error("function getMinerStatus_nbminer exception. msg: " + str(e))
		logging.exception(e)
	return None

def getMinerStatus_gminer(msdict):
	try:
		minerstatus = {}
		minerstatus['uptime'] = msdict['uptime']
		minerstatus['hashrate'] = []
		minerstatus['totalhashrate'] = 0.0
		for device in msdict['devices']:
			minerstatus['hashrate'].append(device['speed'])
			minerstatus['totalhashrate'] += float(device['speed'])
		return minerstatus
	except Exception as e:
		logging.error("function getMinerStatus_gminer exception. msg: " + str(e))
		logging.exception(e)
	return None

def getMinerStatus_ewbfminer(msdict):
	try:
		minerstatus = {}
		minerstatus['uptime'] = 0
		minerstatus['hashrate'] = []
		minerstatus['totalhashrate'] = 0.0
		for device in msdict['result']:
			minerstatus['hashrate'].append(device['speed_sps'])
			minerstatus['totalhashrate'] += float(device['speed_sps'])
		return minerstatus
	except Exception as e:
		logging.error("function getMinerStatus_ewbfminer exception. msg: " + str(e))
		logging.exception(e)
	return None

def getMinerStatus_bminer(msdict):
	try:
		minerstatus = {}
		minerstatus['uptime'] = 0
		minerstatus['hashrate'] = []
		minerstatus['totalhashrate'] = 0.0
		for device in msdict['miners'].values():
			minerstatus['hashrate'].append(device['solver']['solution_rate'])
			minerstatus['totalhashrate'] += float(device['solver']['solution_rate'])
		return minerstatus
	except Exception as e:
		logging.error("function getMinerStatus_bminer exception. msg: " + str(e))
		logging.exception(e)
	return None

def getMinerStatus_kbminer(msdict):
	try:
		minerstatus = {}
		minerstatus['uptime'] = 0
		minerstatus['hashrate'] = msdict['hashrates']
		minerstatus['totalhashrate'] = 0.0
		for hashrate in msdict['hashrates']:
			minerstatus['totalhashrate'] += float(hashrate)
		return minerstatus
	except Exception as e:
		logging.error("function getMinerStatus_kbminer exception. msg: " + str(e))
		logging.exception(e)
	return None

def getMinerStatus_hspminer(msdict, aid):
	try:
		minerstatus = {}
		minerstatus['uptime'] = 0
		minerstatus['hashrate'] = []
		minerstatus['totalhashrate'] = 0.0
		devices = msdict['miner'][0]['devices']
		if aid == 13:
			k = 'ae_hash'
		elif aid == 24:
			k = 'beam_hash'
		elif aid == 11:
			k = 'btm_hash'
		elif aid == 12:
			k = 'eth_hash'
		elif aid == 25:
			k = 'grin_hash'
		else:
			k = 'eth_hash'
		for device in devices:
			minerstatus['totalhashrate'] += float(device[k])
		return minerstatus
	except Exception as e:
		logging.error("function getMinerStatus_hspminer exception. msg: " + str(e))
		logging.exception(e)
	return None

def getMinerStatus_lolminer(msdict):
	try:
		minerstatus = {}
		minerstatus['uptime'] = 0
		minerstatus['hashrate'] = []
		minerstatus['totalhashrate'] = 0.0
		for device in msdict['GPUs']:
			minerstatus['hashrate'].append(float(device['Performance']))
			minerstatus['totalhashrate'] += float(device['Performance'])
		return minerstatus
	except Exception as e:
		logging.error("function getMinerStatus_lolminer exception. msg: " + str(e))
		logging.exception(e)
	return None

def getMinerStatus_wildrigminer(msdict):
	try:
		minerstatus = {}
		minerstatus['uptime'] = 0
		minerstatus['hashrate'] = []
		minerstatus['totalhashrate'] = 0.0
		for hashrate in msdict['hashrate']['threads']:
			minerstatus['hashrate'].append(hashrate[0])
			minerstatus['totalhashrate'] += float(hashrate[0])
		return minerstatus
	except Exception as e:
		logging.error("function getMinerStatus_wildrigminer exception. msg: " + str(e))
		logging.exception(e)
	return None

def getMinerStatus_srbminer(msdict):
	try:
		minerstatus = {}
		minerstatus['uptime'] = 0
		minerstatus['hashrate'] = []
		minerstatus['totalhashrate'] = 0.0
		for device in msdict['devices']:
			minerstatus['hashrate'].append(device['hashrate'])
			minerstatus['totalhashrate'] += float(device['hashrate'])
		return minerstatus
	except Exception as e:
		logging.error("function getMinerStatus_srbminer exception. msg: " + str(e))
		logging.exception(e)
	return None

def getMinerStatus_xmrigminer(msdict):
	try:
		minerstatus = {}
		minerstatus['uptime'] = 0
		minerstatus['hashrate'] = []
		minerstatus['totalhashrate'] = 0.0
		for hashrate in msdict['hashrate']['threads']:
			minerstatus['hashrate'].append(hashrate[0])
			minerstatus['totalhashrate'] += float(hashrate[0])
		return minerstatus
	except Exception as e:
		logging.error("function getMinerStatus_wildrigminer exception. msg: " + str(e))
		logging.exception(e)
	return None

#tcp

def getMinerStatus_claymoreminer(msdict):
	try:
		minerstatus = {}
		minerstatus['uptime'] = msdict['result'][1]
		minerstatus['hashrate'] = []
		minerstatus['totalhashrate'] = 0.0
		for hashrate in msdict['result'][3].split(';'):
			minerstatus['hashrate'].append(float(hashrate)*1000)
			minerstatus['totalhashrate'] += (float(hashrate)*1000)
		return minerstatus
	except Exception as e:
		logging.error("function getMinerStatus_wildrigminer exception. msg: " + str(e))
		logging.exception(e)
	return None

def getMinerStatus_CryptoDredgeMiner(buf):
	try:
		minerstatus = {}
		minerstatus['uptime'] = 0
		minerstatus['hashrate'] = []
		minerstatus['totalhashrate'] = 0.0
		for i in range(16):
			for sline in buf.split('|'):
				if 'GPU='+str(i)+';' in sline:
					hashrate = float(sline.split(';')[2].split('=')[1])
					minerstatus['hashrate'].append(hashrate)
					minerstatus['totalhashrate'] += float(hashrate)
					break
		return minerstatus
	except Exception as e:
		logging.error("function getMinerStatus_CryptoDredgeMiner exception. msg: " + str(e))
		logging.exception(e)
	return None

def getMinerStatus_TeamRedMiner(buf):
	try:
		minerstatus = {}
		minerstatus['uptime'] = 0
		minerstatus['hashrate'] = []
		minerstatus['totalhashrate'] = 0.0
		for sline in buf.split('|'):
			if 'MHS av' in sline:
				for l in sline.split(','):
					if 'MHS av' in l:
						hashrate = float(l.split('=')[1]) * 1000000
						minerstatus['hashrate'].append(hashrate)
						minerstatus['totalhashrate'] += float(hashrate)
		return minerstatus
	except Exception as e:
		logging.error("function getMinerStatus_TeamRedMiner exception. msg: " + str(e))
		logging.exception(e)
	return None

def getMinerStatus_ZEnemyMiner(buf):
	try:
		minerstatus = {}
		minerstatus['uptime'] = 0
		minerstatus['hashrate'] = []
		minerstatus['totalhashrate'] = 0.0
		for sline in buf.split('|'):
			for l in sline.split(';'):
				if 'KHS=' in l:
					hashrate = float(l.split('=')[1]) * 1000.0
					minerstatus['hashrate'].append(hashrate)
					minerstatus['totalhashrate'] += float(hashrate)
		return minerstatus
	except Exception as e:
		logging.error("function getMinerStatus_ZEnemyMiner exception. msg: " + str(e))
		logging.exception(e)
	return None

def checkMinerApiPort(port):
	try:
		with os.popen('netstat -lnt') as p:
			lines = p.read().splitlines(False)
			for line in lines:
				if str(port) in line:
					return True
	except Exception as e:
		logging.error("function checkMinerApiPort exception. msg: " + str(e))
		logging.exception(e)
	return False

def getMinerResultDict_url(url):
	try:
		_url = urlparse(url)
		if checkMinerApiPort(_url.port):
			req = request.Request(url)
			with request.urlopen(req) as f:
				return json.loads(f.read().decode('utf-8'))
		else:
			logging.error('miner url api port unready.')
		
	except Exception as e:
		logging.error("function getMinerResultDict_url exception. msg: " + str(e))
		logging.exception(e)
	return None

def getMinerStatus_url(apicfg):
	try:
		apimode = apicfg['apimode']
		url = apicfg['apiurl']
		msdict = getMinerResultDict_url(url)
		if msdict:
			logging.info('URL: get miner hashrate ok!\n' + str(msdict))
			status = None
			if apimode == 1:
				status = getMinerStatus_trex(msdict)
			elif apimode == 10 or apimode == 35:
				status = getMinerStatus_nbminer(msdict)
			elif apimode == 8 or apimode == 33:
				status = getMinerStatus_gminer(msdict)
			elif apimode == 9:
				status = getMinerStatus_ewbfminer(msdict)
			elif apimode == 7 or apimode == 34:
				status = getMinerStatus_bminer(msdict)
			elif apimode == 29:
				status = getMinerStatus_kbminer(msdict)
			elif apimode == 11:
				status = getMinerStatus_hspminer(msdict, 11)
			elif apimode == 12:
				status = getMinerStatus_hspminer(msdict, 12)
			elif apimode == 13:
				status = getMinerStatus_hspminer(msdict, 13)
			elif apimode == 24:
				status = getMinerStatus_hspminer(msdict, 24)
			elif apimode == 25:
				status = getMinerStatus_hspminer(msdict, 25)
			elif apimode == 17:
				status = getMinerStatus_lolminer(msdict)
			elif apimode == 15:
				status = getMinerStatus_wildrigminer(msdict)
			elif apimode == 14:
				status = getMinerStatus_srbminer(msdict)
			elif apimode == 28:
				status = getMinerStatus_xmrigminer(msdict)
			elif apimode == 30:
				status = getMinerStatus_xmrigminer(msdict)
			return status
	except Exception as e:
		logging.error("function getMinerStatus_url exception. msg: " + str(e))
		logging.exception(e)
	return None

def getMinerResult_tcp(url):
	try:
		cmd = url.split('|')[0] +'\r\n'
		port = url.split('|')[1]
		if checkMinerApiPort(port):
			sock = socket.create_connection(('127.0.0.1', port), 3)
			sock.setblocking(True)
			sock.settimeout(None)
			sock.sendall(cmd.encode())
			buf = sock.recv(10240).decode()
			sock.close()
			return buf
		else:
			logging.error('miner tcp api port unready.')
		
	except Exception as e:
		logging.error("function getMinerResultDict_tcp exception. msg: " + str(e))
		logging.exception(e)
	return None

def getMinerStatus_tcp(apicfg):
	try:
		apimode = apicfg['apimode']
		url = apicfg['apiurl']
		buf = getMinerResult_tcp(url)
		if buf:
			logging.info('TCP: get miner hashrate ok!\n' + str(buf))
			status = None
			if apimode == 4:
				status = getMinerStatus_ZEnemyMiner(buf)
			elif apimode == 5:
				status = getMinerStatus_CryptoDredgeMiner(buf)
			elif apimode == 26:
				status = getMinerStatus_TeamRedMiner(buf)
			elif apimode == 3 or apimode == 28 or apimode == 30:
				msdict = json.loads(buf)
				status = getMinerStatus_claymoreminer(msdict)
			return status
	except Exception as e:
		logging.error("function getMinerStatus_tcp exception. msg: " + str(e))
		logging.exception(e)
	return None

def getMinerStatus(apicfg):
	try:
		apimode = apicfg['apimode']
		tcpmode = [3, 4, 5, 26,28, 30]
		if apimode in tcpmode:
			return getMinerStatus_tcp(apicfg)
		else:
			return getMinerStatus_url(apicfg)
	except Exception as e:
		logging.error("function getMinerStatus exception. msg: " + str(e))
		logging.exception(e)
	return None

if __name__ == '__main__':
    pass
