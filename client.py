import time
from urllib import response
import requests
import os
from hashlib import md5
import json
import random
import subprocess

class HttpClient():
    def __init__(self):
        self.times = 0
        with open('./clienttest.json','r',encoding = 'utf-8') as SendData:
            SendJson = json.load(SendData)
        self.IP = SendJson['IP']
        print(self.IP)
        SendData.close()

        URL = "http://" + self.IP + "/sendjson"
        response = requests.post(URL)
        print(response.status_code)
        if response.status_code == 200:
            self.dev = json.loads(response.text)
            print(self.dev)

    def get_first_down(self):
        filepath = './test'
        if not os.path.exists(filepath):
            cmd_str = f'dd if=./ of=test bs=1M count=0 seek=1000'
            subprocess.getoutput(cmd_str.encode('utf8'))
            with open('./clienttest.json', 'r', encoding='utf-8') as SendData:
                SendJson = json.load(SendData)
                SendJson['MD5'] = self.MD5_test()
            SendData.close()
            with open('./clienttest.json', 'w+', encoding='utf-8') as SendData:
                json.dump(SendJson, SendData)
        else:
            with open('./clienttest.json', 'r', encoding='utf-8') as SendData:
                SendJson = json.load(SendData)
                SendJson['MD5'] = self.MD5_test()
            SendData.close()
            with open('./clienttest.json', 'w+', encoding='utf-8') as SendData:
                json.dump(SendJson, SendData)

    def MD5_test(self):
        cmd_str = f'md5sum test'
        a = subprocess.getoutput(cmd_str.encode('utf8'))
        a = a.split()[0]
        return a

    def get_file(self, filepath):
        if not os.path.exists(filepath):
            URL = 'http://' + self.IP + "/download/" + self.dev['down_file_size']
            print(URL)
            response = requests.post(URL)
            print(response.status_code)
            if response.status_code == 200:
                f = open('./new_file/text.txt', 'w+',encoding = 'utf-8')
                f.write(response.text)
                f.close()
                os.remove(filepath)
        else:
            print('Error! File already exists')

    def check_file(self):
        with open('./clienttest.json', 'r') as SendData:
            SendJson = json.load(SendData)
        if SendJson['MD5'] == self.MD5_test():
            SendJson['result'] = 0
        else:
            SendJson['result'] = 1
        SendJson['times'] += 1
        print(SendJson)
        URL = "http://" + self.IP + "/verification"
        print(URL)
        response = requests.post(URL, json=SendJson)
        if response.status_code == 200:
            print('send OK')
        with open('./clienttest.json', 'w') as f:
            json.dump(SendJson, f)


if __name__ == '__main__':
    http = HttpClient()
    http.get_first_down()
    http.check_file()
    while True:
        times = random.randint(0, 10)
        time.sleep(times)
        http.get_file('./new_file/text.txt')
    

