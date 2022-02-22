import time
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
        with open('./test.json','r') as TestData:
            TestJson = json.load(TestData)
            self.times = TestJson['times']
            self.firstFileSize = TestJson['first_file']
            print(self.times)
            print(self.firstFileSize)
        TestData.close()



    def get_first_down(self):
        filepath = './new_file/firstTXT.txt'
        #查找本地路径上的firstTXT.txt是否存在
        if not os.path.exists(filepath):
            URL = "http://"+self.IP+"/firstdownload/"+"self.firstFileSize"
            print(URL)
            #直接POST上去，返回文件
            response = requests.post(URL)
            print(response.status_code)
            if response.status_code == 200:
                #如果下载成功则将下载下来的文件写入文件中
                f = open('./new_file/firstTXT.txt','w+')
                f.write(response.text)
                f.close()
                #然后取读json文件
                with open('./clienttest.json', 'r') as SendData:
                    SendJson = json.load(SendData)
                #得到1GB.txt的MD5
                SendJson['MD5'] = self.MD5_test('./new_file/firstTXT.txt')
                SendData.close()
                with open('./clienttest.json', 'w') as f:
                    #把MD5写入clienttest.json文件里
                    json.dump(SendJson,f)
        else:
            print('文件存在')
            #需要检查文件的大小
            file_stats = os.stat(filepath)
            with open('./test.josn','r') as TestData:
                TestJson = json.load(TestData)
            #判断文件其大小
            if TestJson['first_file'] != file_stats.st_size:
                TestJson['first_file'] = file_stats.st_size
                json.dump(TestJson,TestData)
                TestData.close()
            else:
                print('文件尺寸大小正常')

    def MD5_test(self,filepath):
        f = open(filepath, 'rb')

        hash = md5()
        #得到该文件
        hash.update(f.read())
        f.close()
        return hash.hexdigest()

    def get_file(self,filepath):
        if not os.path.exists(filepath):
            URL = 'http://'+self.IP+"/download"
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
        ######问题:为什么不统计成功与失败的次数
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
    '''
    http.get_first_down()
    http.check_file('./new_file/1GB.txt')
    while True:
        times = random.randint(10, 300)
        time.sleep(times)
        http.get_file('./new_file/text.txt')
    '''
