
from tools import *
import logging

logging.basicConfig(level = logging.INFO, format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt = '%Y-%m-%d  %H:%M:%S %a')

'''循环检测云端指令是否需要重启系统'''
while True:
    try:
        url = 'http://api.lsminer.com:37124/redline/' + getWkid()
        logging.info('xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx');
        logging.info(url)
        reboot = getReboot(url)
        if reboot:
            logging.warning('recv reboot cmd! system will be reboot.')
            os.system("sudo reboot")
        else:
            print('sleep 60 seconds. and check reboot cmd.')
            time.sleep(60)
    except Exception as e:
        logging.error("main loop run exception. msg: " + str(e))
        logging.error("sleep 3 seconds and retry.")
        logging.exception(e)
        time.sleep(3)

