import asyncio
import json
import re
import subprocess
import threading

from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer
from channels.exceptions import StopConsumer

class ChatConsumer(WebsocketConsumer):
    def websocket_connect(self, message):
        print("有人来连接了...")
        # 有客户端向服务器发送websocket请求的时候自动触发
        self.accept() # 服务端允许创建连接

        # 主动给客户端发送消息
        self.send("初始化成功...............")

    def websocket_receive(self, message):
        # 浏览器基于websocket向后端发送数据，自动触发接受数据
        text = message['text']
        print("接收到了消息 ->", text)

        # res = "{} CoffeeTau".format(text)
        # self.send(res)
        if text == 'restart':
            self.send("进行重启")

            # 启动后台进程并实时读取输出
            self.process = subprocess.Popen(
                'su - dmdba -c "cd /home/dmdba/dmdbms/bin/DmServiceDAMENG/ && restart"',
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # 启动线程读取后台进程的输出
            self.thread = threading.Thread(target=self.read_output)
            self.thread.start()

        if text == 'partition':
            self.send("创建分区表")

            # 启动后台进程并实时读取输出
            self.process = subprocess.Popen(
                'su - dmdba -c "cd /home/dmdba/benchmarksql-5.0/run/ && ./runSQL.sh ./props_table.dm ../sqlCreateTable.sql"',
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # 启动线程读取后台进程的输出
            self.thread = threading.Thread(target=self.read_output)
            self.thread.start()

        if text == 'load':
            self.send("加载数据")

            # 启动后台进程并实时读取输出
            self.process = subprocess.Popen(
                'su - dmdba -c "cd /home/dmdba/benchmarksql-5.0/run/ && ./runLoader.sh ./props.dm"',
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # 启动线程读取后台进程的输出
            self.thread = threading.Thread(target=self.read_output)
            self.thread.start()

        if text == 'index':
            self.send("创建索引")

            # 启动后台进程并实时读取输出
            self.process = subprocess.Popen(
                'su - dmdba -c "cd /home/dmdba/benchmarksql-5.0/run/ && ./runSQL.sh ./props.dm ../sqlCreateIndex.sql"',
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # 启动线程读取后台进程的输出
            self.thread = threading.Thread(target=self.read_output)
            self.thread.start()

        if text == 'benchmark':
            self.send("开始压测")

            # 启动后台进程并实时读取输出
            self.process = subprocess.Popen(
                'su - dmdba -c "cd /home/dmdba/benchmarksql-5.0/run/ && ./runBenchmark.sh ./props.dm"',
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # 启动线程读取后台进程的输出
            self.thread = threading.Thread(target=self.read_output)
            self.thread.start()

        if text == 'stop':
            self.send("停止压测")



            self.process.terminate()  # 终止后台进程
            self.thread.join()  # 等待线程结束

            # # 启动后台进程并实时读取输出
            # self.process = subprocess.Popen(
            #     'su - dmdba -c "ps -ef | grep \'./props.dm\' | grep -v grep | awk \'{print $2}\'"',
            #     shell=True,
            #     stdout=subprocess.PIPE,
            #     stderr=subprocess.PIPE,
            #     text=True
            # )
            #
            # # 启动线程读取后台进程的输出
            # self.thread = threading.Thread(target=self.read_output)
            # self.thread.start()

        '''
        self.close()
        服务端主动关闭连接，会给客户端发断开连接的消息，客户端的socket.unclose函数会激活
        同时服务器也会执行websocket_disconnect函数
        如果服务器执行了raise StopConsumer()，那就不会执行websocket_disconnect函数
        '''

    def websocket_disconnect(self, message):
        # 客户端主动与服务器断开连接，自动触发
        print("客户端断开连接")
        self.process.terminate()  # 终止后台进程
        self.thread.join()  # 等待线程结束
        raise StopConsumer()  # 服务端同意断开连接

    def read_output(self):
        for line in iter(self.process.stdout.readline, ''):
            if line:
                # 发送后台进程输出到前端
                self.send(text_data=json.dumps({
                    'message': line.strip()
                }))
        self.process.stdout.close()
        self.process.wait()



