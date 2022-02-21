from flask import Flask, request
import random
import os
import serial
import json
from modbus_tk.modbus_rtu import *
import modbus_tk.defines as cst
import logging
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)

#随机生成TXT文件
def generateTXTFile(type):
    if int(type) == 0:
        size = 1024
        filename = '1GB.txt'
    else:
        size = random.randint(0,150)
        filename = 'text.txt'
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
@app.route('/hello')
def hello():
    return 'hello！'
#反馈校验测数
@app.route('/verification', methods=['POST'])
def verification():
    print(request.json)
    RecvJson = request.json
    if RecvJson['result'] != 0:
        logging.info('verification error')
    else:
        logging.info('verification success')
    return {}

@app.route('/sendjson', methods=['POST'])
def sendjson():
    with open('./test.json', 'r', encoding='utf-8') as SendData:
        SendJson = json.load(SendData)
    SendJsons = json.dumps(SendJson)
    return SendJsons
#由客户端发送指令，随机给取文件 以及文件大小
@app.route('/download', methods=['POST'])
def download():
    #随机生成文件大小
    generateTXTFile(1)
    f = open('./file/text.txt','rb')
    tmp = f.read()
    f.close()
    if os.path.exists('./file/text.txt'):
        os.remove('./file/text.txt')
    return tmp

#
@app.route('/firstdownload', methods=['POST'])
def firstdownload():
    filepath = './file/1GB.txt'
    if not os.path.exists(filepath):
        generateTXTFile(0)
    f = open('./file/1GB.txt','rb')
    tmp = f.read()
    f.close()
    return tmp


def device_run():
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

    while True:

        times = random.randint(10, 300)
        time.sleep(times)
        rtu_exec(1, cst.WRITE_SINGLE_REGISTER, 20492, output_value=1)
        time.sleep(20)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,filename='log.log',filemode='a',format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s')
    #app.run(host='0.0.0.0',port=6667, debug=True)

    # devicePool = ThreadPoolExecutor(max_workers=1)
    # devicePool.submit(device_run)
    app.run()

