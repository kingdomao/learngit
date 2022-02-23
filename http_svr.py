from distutils.log import debug
from pickle import GET
from sre_constants import FAILURE
from flask import Flask, request,jsonify
import random
import os
#from numpy import size
import serial
import json
from modbus_tk.modbus_rtu import *
import modbus_tk.defines as cst
import logging
from concurrent.futures import ThreadPoolExecutor

appflasktest = Flask(__name__)


Gtimes = 0


def generateTXTFile(type):
    if int(type) == 0:
        size = 1024
        filename = 'firstTXT.txt'
    else:
        size = random.randint(0,150)
        filename = 'TXT.txt'
    logging.info(f'{filename}')
    filepath = './file/'
    f = open(filepath + filename, 'w',encoding='utf-8')
    for i in range(size):
        if i >= 100:
            if i % 100 == 0:
                a = 1
        for j in range(1024):
            try:
                f.write('01' * 512)
            except KeyboardInterrupt:
                logging.info('\n:KeyboardInterrupt')
                f.close()
                exit(-1)
    f.close()


def generateSizeTXTFile(type,size):
    if int(type) == 0:
        filename = 'firstTXT.txt'
    else:
        filename = 'TXT.txt'
    logging.info(f'{filename}')
    filepath = './file/'
    f = open(filepath + filename, 'w',encoding='utf-8')
    for i in range(size):
        if i >= 100:
            if i % 100 == 0:
                logging.info(f'i // {100 * 100}MB.')
        for j in range(1024):
            try:
                f.write('01' * 512)
            except KeyboardInterrupt:
                logging.info('\n:KeyboardInterrupt')
                f.close()
                exit(-1)
    f.close()




@appflasktest.route('/')
def hello_world():
    return '!!!hello world!!!---'

@appflasktest.route('/hello/<id>',methods=['POST'])
def hello(id):
    if id == '1':
        return 'hello'
    elif id == '2':
        return '1111'
    else:
        return '?'


@appflasktest.route('/verification', methods=['POST'])
def verification():
    print(request.json)
    RecvJson = request.json
    if RecvJson['result'] != 0:
        logging.info(f"{RecvJson['times']}:verification error")
    else:
        logging.info(f"{RecvJson['times']}:verification success")
    return {}

@appflasktest.route('/sendjson', methods=['POST'])
def sendjson():
    with open('./test.json', 'r', encoding='utf-8') as SendData:
        SendJson = json.load(SendData) 
    SendJsons = json.dumps(SendJson)   
    return SendJsons

@appflasktest.route('/download/<size>', methods=['POST'])
def download(size):
    if size == '0':
        print('file size is 0 FAILURE download')
    else:
        size = int(size)
        ran_size = random.randint(1,size)
        generateSizeTXTFile(1,ran_size)
        f = open('./file/TXT.txt','rb')
        tmp = f.read()
        f.close()
    if os.path.exists('./file/TXT.txt'):
        os.remove('./file/TXT.txt')
    return tmp

def device_run():

    releas_p = 1
    com = serial.Serial()
    com.port = "/dev/ttyUSB1"
    com.baudrate = 9600
    com.stopbits = 1
    com.bytesize = 8
    com.parity = 'N'
    rtu = RtuMaster(com)
    rtu.set_timeout(5)
    com.open()
    def rtu_exec(slave, opcode, start_addr, **kwargs):
        try:
            resp = rtu.execute(slave, opcode, start_addr, **kwargs)
            logging.info('response:{}'.format(resp))
            time.sleep(2)
            rtu.close()
            return resp
        except Exception as e:
            logging.info('caught exception:{}'.format(e))


    with open('./test.json','r',encoding='utf-8') as TestData:
        TestJson = json.load(TestData)
    TT = TestJson['times']
    TestData.close()
    #times = random.randint(10, 300)
    #time.sleep(times)
    while releas_p:
        time_T = random.randint(10,20)

        logging.info(f'Power is expected to be OFF in {time_T} s')
        #time.sleep(time_T)
        time.sleep(60)
        rtu_exec(1, cst.WRITE_SINGLE_REGISTER, 16384, output_value=0x0)
        time_T = random.randint(10,300)
        logging.info(f'The power supply will be cut off for {time_T} s')
        #time.sleep(time_T)
        time.sleep(60)
        rtu_exec(1, cst.WRITE_SINGLE_REGISTER, 16384, output_value=0x01)
        time_T = random.randint(10,300)
        logging.info(f'The power supply will last for {time_T} s')
        #time.sleep(time_T)
        time.sleep(60)
        logging.info(f"Test power-on and power-off times reduced by one -> {TT} times")
        TT = TT - 1
        if TT == 0:
            releas_p = 0
            logging.info('The power-on and power-off test is complete')


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,filename='log.log',filemode='a',format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s')
    devicePool = ThreadPoolExecutor(max_workers=1)
    logging.info("success start")
    devicePool.submit(device_run)
    appflasktest.run(host='0.0.0.0',port=6667)
    #device_run()
    logging.info("test end!!")

