from pickle import GET
from sre_constants import FAILURE
from flask import Flask, request
import random
import os
from numpy import size
import serial
import json
from modbus_tk.modbus_rtu import *
import modbus_tk.defines as cst
import logging
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)


Gtimes = 0

#随机生成TXT文件
def generateTXTFile(type):
    if int(type) == 0:
        size = 1024
        filename = 'firstTXT.txt'
    else:
        size = random.randint(0,150)
        filename = 'TXT.txt'
    logging.info(f'文件名：{filename}')
    filepath = './file/'
    f = open(filepath + filename, 'w')
    for i in range(size):
        if i >= 100:
            if i % 100 == 0:
                logging.info(f'已生成{i // 100 * 100}MB数据.')
        for j in range(1024):
            try:
                f.write('01' * 512)
            except KeyboardInterrupt:
                logging.info('\n异常中断:KeyboardInterrupt')
                f.close()
                exit(-1)
    f.close()

#生成size大小且名为TXT文件
def generateSizeTXTFile(type,size):
    if int(type) == 0:
        filename = 'firstTXT.txt'
    else:
        filename = 'TXT.txt'
    logging.info(f'文件名：{filename}')
    filepath = './file/'
    f = open(filepath + filename, 'w')
    for i in range(size):
        if i >= 100:
            if i % 100 == 0:
                logging.info(f'已生成{i // 100 * 100}MB数据.')
        for j in range(1024):
            try:
                f.write('01' * 512)
            except KeyboardInterrupt:
                logging.info('\n异常中断:KeyboardInterrupt')
                f.close()
                exit(-1)
    f.close()



#测试flask路由
@app.route('/')
def hello_world():
    return '!!!hello world!!!---'

@app.route('/hello/<id>',methods=['POST'])
def hello(id):
    if id == '1':
        return 'hello！'
    elif id == '2':
        return '1111'
    else:
        return '?'

#反馈校验测数
@app.route('/verification', methods=['POST'])
def verification():
    print(request.json)
    RecvJson = request.json
    if RecvJson['result'] != 0:
        logging.info(f"{RecvJson['times']}:verification error")
        print(f"{RecvJson['times']}:verification error")
    else:
        logging.info(f"{RecvJson['times']}:verification success")
        print(f"{RecvJson['times']}:verification success")
    return {}

@app.route('/sendjson', methods=['POST'])
def sendjson():
    with open('./test.json', 'r', encoding='utf-8') as SendData:
        SendJson = json.load(SendData)  #json文件-> python字典
    SendJsons = json.dumps(SendJson)    #python字典 -> json字符串
    return SendJsons

#由客户端发送指令，随机给取文件 以及文件大小
@app.route('/download/<size>', methods=['POST'])
def download(size):
    if size == '0':
        print('file size is 0 FAILURE download')
    else:
        size = int(size)
        generateTXTFile(size)
        f = open('./file/TXT.txt','rb')
        tmp = f.read()
        f.close()
    if os.path.exists('./file/TXT.txt'):
        os.remove('./file/TXT.txt')
    return tmp

def device_run():
    global Gtimes
    releas_p = 1
        
    def rtu_exec(slave, opcode, start_addr, **kwargs):
        com = serial.Serial()
        com.port = "/dev/ttyS6"
        com.baudrate = 9600
        com.stopbits = 1
        com.bytesize = 8
        com.parity = 'N'
        #设定串口为从站
        rtu = RtuMaster(com)
        rtu.set_timeout(5)
        try:
            com.open()
            #发送数据到从机
            resp = rtu.execute(slave, opcode, start_addr, **kwargs)
            logging.info('response:{}'.format(resp))
            # rtu.close()
            return resp
        except Exception as e:
            logging.info('caught exception:{}'.format(e))

    while releas_p:
        #还得改光电盒没用过
        with open('./test.json','r') as TestData:
            TestJson = json.load(TestData)
        TT = TestJson['times']
        TestData.close()
        times = random.randint(10, 300)
        time.sleep(times)
        rtu_exec(1, cst.WRITE_SINGLE_REGISTER, 20492, output_value=1)
        time.sleep(20)
        if TT == 0:
            with open('./test.json','w') as TestData:
                TestJson = json.load(TestData)
                TestJson['times'] = 0
                json.dump(TestJson,TestData)
            releas_p = 0
            print("test End")
            logging.info('test End')
        TT = TT - 1

app.route('/sendjson', methods=['POST'])
def sendjson():
    with open('./test.json', 'r', encoding='utf-8') as SendData:
        SendJson = json.load(SendData)  #json文件-> python字典
    SendJsons = json.dumps(SendJson)    #python字典 -> json字符串
    return SendJsons




if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,filename='log.log',filemode='a',format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s')
    app.run(host='0.0.0.0',port=6667, debug=True)

    # devicePool = ThreadPoolExecutor(max_workers=1)
    # devicePool.submit(device_run)
    app.run()

