import time
from urllib import response
import requests
import os
from hashlib import md5
import json
import random

#客户端
class HttpClient():
    def __init__(self):
        self.times = 0
        with open('./clienttest.json', 'r') as SendData:
            SendJson = json.load(SendData)
        self.IP = SendJson['IP']
        #临时服务器(http_srv.py中路由的IP)
        print(self.IP)
        SendData.close()

        URL = "http://"+self.IP+"/sendjson"
        response = requests.post(URL)
        print(response.status_code)
        if response.status_code == 200:
            self.dev = json.loads(response.text)
            print(self.dev)

    def get_first_down(self):
        def generateTXTFile(type):
            if int(type) == 0:
                size = 1024
                filename = 'firstTXT.txt'
            else:
                size = random.randint(0,150)
                filename = 'TXT.txt'
            print(f'文件名：{filename}')
            filepath = './file/'
            f = open(filepath + filename, 'w')
            for i in range(size):
                if i >= 100:
                    if i % 100 == 0:
                        print(f'已生成{i // 100 * 100}MB数据.')
                        for j in range(1024):
                            try:
                                f.write('01' * 512)
                            except KeyboardInterrupt:
                                print('\n异常中断:KeyboardInterrupt')
                                f.close()
                                exit(-1)
            f.close()

        filepath = './file/firstTXT.txt'
        if not os.path.exists(filepath):
            generateTXTFile(0)
            with open('./clienttest.json', 'r') as SendData:
                SendJson = json.load(SendData)
                SendJson['MD5'] = self.MD5_test('./file/firstTXT.txt')
                SendData.close()
                with open('./clienttest.json', 'w') as f:
                    json.dump(SendJson,f)
        else:
            print('文件存在')

    def MD5_test(self,filepath):
        f = open(filepath, 'rb')
        hash = md5()
        #得到该文件
        hash.update(f.read())
        f.close()
        return hash.hexdigest()

    def get_file(self,filepath):
        if not os.path.exists(filepath):
            URL = 'http://'+self.IP+"/download/"+self.dev['down_file_size']
            print(URL)
            response = requests.post(URL)
            print(response.status_code)
            if response.status_code == 200:
                f = open('./new_file/text.txt', 'w+')
                f.write(response.text)
                f.close()
                os.remove(filepath)
        else:
            print('Error! File already exists')


    def check_file(self,filepath):
        with open('./clienttest.json', 'r') as SendData:
            SendJson = json.load(SendData)
        if SendJson['MD5'] == self.MD5_test(filepath):
            SendJson['result'] = 0
        else:
            SendJson['result'] = 1
        SendJson['times'] += 1
        print(SendJson)
        URL = "http://"+ self.IP+"/verification"
        print(URL)
        #一直在发送给服务端
        response = requests.post(URL,json=SendJson)
        if response.status_code == 200:
            print('send OK')
        with open('./clienttest.json', 'w') as f:
            #python转json 并传入文件中
            json.dump(SendJson, f)

if __name__ == '__main__':
    http = HttpClient()
    http.get_first_down()
    http.check_file('./file/firstTXT.txt')
    '''
    while True:
        times = random.randint(10, 300)
        time.sleep(times)
        http.get_file('./new_file/text.txt')
    '''
