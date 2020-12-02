import socket
import easygui as eg
import json
import os
import time

'''读取配置文件'''
f = open('clientconf.json', 'r', encoding='utf-8')
date = json.load(f)
ip = date.get('IP')
port = date.get('port')
f.close()

'''创建socket对象'''
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    '''连接服务器， 指定IP和端口'''
    client.connect((ip, port))

    '''接收小于 1024 字节的数据'''
    msg = client.recv(1024)

    '''输出连接成功信息'''
    print(msg.decode('utf-8'))
except Exception as e:
    print(f'连接服务器失败', e)
else:
    '''选择发送的文件'''
    filepath = eg.fileopenbox(title='选择文件')
    '''获取文件名,文件大小'''
    filename = filepath.split("\\")[-1]
    filesize = os.path.getsize(filepath)
    # 先将文件名传过去
    # 编码文件名
    client.send(filename.encode())
    time.sleep(0.5)
    # 再将将文件大小传过去
    # 编码文件大小
    client.send(filesize.to_bytes(filesize.bit_length(), byteorder='big'))
    try:
        '''传输文件'''
        start_time = time.time()
        with open(filepath, 'rb') as f:
            size = 0
            while True:
                #读取文件数据，每次1024KB
                f_data = f.read(1024)
                # 数据长度不为零，传输继续
                if f_data:
                    client.send(f_data)
                    size += len(f_data)
                    if time.time() - start_time == 0:
                        time.sleep(0.5)
                    speed = (size) / (time.time() - start_time)
                    print('\r' + '【上传进度】:%s%.2f%%, Speed: %.2fMB/s' % ('>' * int(size * 50 / filesize), float(size / filesize * 100), float(speed / 1024 / 1024)), end=' ')
                # 数据长度为零传输完成
                else:
                    print(f'{filename},{float(filesize/1024/1024):.2f}MB, 传输完成')
                    break
    except Exception as e:
        print(f'传输异常', e)
finally:
    '''关闭客户端'''
    client.close()