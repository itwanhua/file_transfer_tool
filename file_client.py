#!/usr/bin/python3
# -*- coding: utf-8 -*-

import socket
import sys
import os
import hashlib

'''
文件传输客户端
'''

def get_file_md5(file_path):
    '''
    功能：获取文件MD5值，用于文件校验
    参数：文件路径
    '''
    m = hashlib.md5()
    with open(file_path, "rb") as f:
        while True:
            data = f.read(1024)
            if len(data) == 0:
                break    
            m.update(data)   
    return m.hexdigest().upper()


# 从配置文件中获取服务器地址
congfig_path = os.path.join(os.path.split(os.path.realpath(__file__))[0], "config.ini")
with open(congfig_path, "r") as f:
    data = f.read()
    server_ip = data.split(":")[0]
    server_port = int(data.split(":")[1])

sock = socket.socket() # 创建套接字
sock.connect((server_ip, server_port)) # 连接服务器

while True:
    # 从报头中提取信息
    file_path = sock.recv(300).decode().rstrip() 
    if len(file_path) == 0:
        break

    file_size = sock.recv(15).decode().rstrip()
    if len(file_size) == 0:
        break
    file_size = int(file_size)

    file_md5 = sock.recv(32).decode()
    if len(file_md5) == 0:
        break

    # 如果为空文件夹
    if file_size == -1:
        print("\n成功接收空文件夹 %s" % file_path)
        os.makedirs(file_path, exist_ok=True)
        continue

    # 若文件上层目录不存在则创建，存在继续执行下面代码
    os.makedirs(os.path.dirname(file_path), exist_ok=True) 

    print("\n正在接收文件 %s，请稍候......" % file_path)

    f = open(file_path, "wb")
    recv_size = 0 # 根据接收文件大小来判定是否接收完毕
    while recv_size < file_size:
        file_data = sock.recv(file_size - recv_size)
        if len(file_data) == 0: # 接收数据为空字符串则跳出当前循环
            break

        f.write(file_data)
        recv_size += len(file_data) # 动态更新已接收数据包大小

    f.close()

    recv_file_md5 = get_file_md5(file_path) # 得到接收文件MD5
    # MD5校验
    if recv_file_md5 == file_md5:
        print("成功接收文件 %s" % file_path)
    else:
        print("接收文件 %s 失败（MD5校验不通过）" % file_path)
        break

sock.close()

