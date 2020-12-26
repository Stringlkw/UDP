
import socket
import os
import json
import threading
import time

'''导入配置文件'''
f = open('serverconf.json', 'r', encoding='utf-8')
date = json.load(f)
dirsave = date.get('dirSave')
port = date.get('port')
f.close()
if not os.path.exists(dirsave):  # 看是否有该文件夹，没有则创建文件夹
    os.mkdir(dirsave)


class UdpServer:
    def __init__(self):
        """ 创建socket对象"""
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        '''获取本地'''
        self.host = socket.gethostname()

        '''设置端口'''
        self.port = port

        '''绑定地址'''
        self.server.bind(("localhost", self.port))  # 绑定监听端口

        '''设置最大连接数， 超过后排队'''
        self.server.listen(12)

        print('服务器已上线\n等待客户端连接...\n')

    def server100(self):
        while True:
            '''建立客户端连接'''
            client, addr = self.server.accept()
            print(f'客户端: {str(addr)}, 连接上服务器')
            msg = f'已连接到服务器{self.host}!\r\n'
            client.send(msg.encode('utf-8'))
            # 有客户端连接后，创建一个线程给客户端
            t1 = threading.Thread(self.taskfilethread(client))
            # 设置线程守护
            t1.setDaemon(True)
            # 启动线程
            t1.start()

    def taskfilethread(self, client):
        """接收文件名,文件大小"""
        filename = client.recv(1024)
        # time.sleep(0.5)
        filesize = client.recv(1024)
        # 解码文件名,文件大小
        filename = filename.decode()
        filesize = int.from_bytes(filesize, byteorder='big')
        '''接收文件'''
        try:
            f = open(dirsave + "\\" + filename, 'wb')
            size = 0
            start_time = time.time()
            while True:
                # 接收数据
                f_data = client.recv(1024)
                # 数据长度不为零，接收继续
                if f_data:
                    f.write(f_data)
                    size += len(f_data)
                    if time.time() - start_time == 0:
                        time.sleep(0.5)
                    speed = (size) / (time.time() - start_time)
                    print('\r' + '【下载进度】:%s%.2f%%, Speed: %.2fMB/s' % (
                        '>' * int(size * 50 / filesize), float(size / filesize * 100), float(speed / 1024 / 1024)),
                          end=' ')
                # 数据长度为零接收完成
                else:
                    break
        except Exception as e:
            print(f'接收异常', e)
        else:
            f.flush()
            print(f'{filename},{float(filesize / 1024 / 1024):.2f}MB, 接收完成')
            f.close()


if __name__ == '__main__':
    server = UdpServer()
    server.server100()
