#!/usr/bin/python3
# -*- coding: utf-8 -*-

import socket
import sys
import os
import re
import hashlib
import json
import getpass
from user_reg_login_i import check_user_passwd, check_user_phone, check_user_email


conf = json.load(open("server_conf.json")) # 从配置文件中获取服务器地址


def get_passwd_md5(passwd):
    '''
    功能：获取密码MD5值
    参数：用户密码
    返回值：密码MD5值
    '''    
    m = hashlib.md5()
    m.update(passwd.encode())
    return m.hexdigest().upper()


def get_file_md5(file_path):
    '''
    功能：获取文件MD5值，用于文件校验
    参数：文件路径
    返回值：文件MD5值
    '''
    m = hashlib.md5()
    with open(file_path, "rb") as f:
        while True:
            data = f.read(1024)
            if len(data) == 0:
                break    
            m.update(data)   
    return m.hexdigest().upper()


def check_name_existed(sock):
    '''
    函数功能：校验用户名
    函数参数：套接字对象
    返回值：校验通过返回用户名，校验不通过返回0，
    '''
    # 输入待校验的用户名
    while True:
        user_name = input("请输入用户名（只能包含英文字母、数字或下划线，长度6~15位）：")

        # 将用户名发给服务器端进行校验（是否存在）
        req = {"op": 3, "args":{"uname": user_name}}
        req = json.dumps(req).encode()
        req_len = "{:<15}".format(len(req))
        sock.send(req_len.encode())
        sock.send(req)

        # 接收用户名校验信息
        recv_size = 0
        data_len = b""
        while recv_size < 15: # 接收15字节退出
            tmp = sock.recv(15-recv_size)
            if not tmp:
                break
            data_len += tmp
            recv_size += len(tmp)

        data_len = data_len.decode().rstrip()

        if data_len:
            data_len = int(data_len)
            recv_size = 0
            json_data = b""
        
        while recv_size < data_len:
            tmp = sock.recv(data_len-recv_size)
            if len(tmp) == 0:
                break
            json_data += tmp
            recv_size += len(tmp)

        json_data = json.loads(json_data.decode())
        if json_data['op'] == 3 and json_data['error_code'] == 0: # 用户名可注册
            return 1
        else:
            return 0


def user_reg(sock):
    '''
    函数功能：注册用户
    函数参数：套接字对象
    返回值：用户注册成功返回1，注册时用户名校验失败返回0，
    '''
    # 输入用户名
    while True:
        user_name = input("请输入用户名（只能包含英文字母、数字或下划线，长度6~15位）：")
        if re.match("\w{6,15}$", user_name):
            break
        print("输入格式有误或该用户名未通过校验！")
                

    # 输入密码
    while True:
        user_passwd = getpass.getpass("请输入密码（只能包含英文字母、数字或下划线，长度6~15位）：")
        if check_user_passwd(user_passwd) == 1:           
            user_passwd2 = getpass.getpass("请确认密码：")
            if user_passwd2 == user_passwd: 
                user_passwd = get_passwd_md5(user_passwd)
                break
            print("两次密码不匹配！")
        else:
            print("密码格式错误！")

    # 输入手机号
    while True:
        user_phone = input("请输入手机号：")
        if check_user_phone(user_phone) == 1:
            break
        else:
            print("手机号格式错误")

    # 输入邮箱
    while True:
        user_email = input("请输入邮箱：")
        if check_user_email(user_email) == 1:           
            break
        print("邮箱格式错误！")

    # 发送注册请求
    req = {"op": 2, "args":{"uname": user_name, "passwd": user_passwd, "phone": user_phone, "email": user_email}}
    req = json.dumps(req)
    req_len = "{:<15}".format(len(req))
    sock.send(req_len.encode())
    sock.send(req.encode())

    # 接收注册响应
    recv_size = 0
    data_len = b""
    while recv_size < 15: # 接收15字节退出
        tmp = sock.recv(15-recv_size)
        if not tmp:
            break
        data_len += tmp
        recv_size += len(tmp)

    data_len = data_len.decode().rstrip()

    if len(data_len) > 0:
        data_len = int(data_len)
        recv_size = 0
        json_data = b""
    
        while recv_size < data_len:
            tmp = sock.recv(data_len-recv_size)
            if len(tmp) == 0:
                break
            json_data += tmp
            recv_size += len(tmp)

        json_data = json.loads(json_data.decode())
        print(json_data)
        if json_data['op'] == 2 and json_data['error_code'] == 0: # 注册成功
            return 1


def user_login(sock):
    '''
    函数功能：登录用户
    函数参数：套接字对象
    '''
    while True:
        user_name = input("\n用户名>>")
        user_passwd = getpass.getpass("密码>>")
        user_passwd = get_passwd_md5(user_passwd)

        # 发送登录请求
        req = {"op": 1, "args":{"uname": user_name, "passwd": user_passwd}}
        req_json = json.dumps(req).encode()
        req_len = "{:<15}".format(len(req_json))
        sock.send(req_len.encode())
        sock.send(req_json)

        # 接收登录响应
        recv_size = 0
        data_len = b""
        while recv_size < 15: # 接收15字节退出
            tmp = sock.recv(15-recv_size)
            if not tmp:
                break
            data_len += tmp
            recv_size += len(tmp)
        data_len = data_len.decode().rstrip()

        if len(data_len) > 0:
            data_len = int(data_len)
            recv_size = 0
            json_data = b""
        
            while recv_size < data_len:
                tmp = sock.recv(data_len-recv_size)
                if len(tmp) == 0:
                    break
                json_data += tmp
                recv_size += len(tmp)

            json_data = json.loads(json_data.decode())
            if json_data['op'] == 1 and json_data['error_code'] == 0: # 登录成功
                print("登录成功！")
                return user_name
            else:
                return 0     


def menu(sock):
    '''
    函数功能：菜单函数
    参数：套接字对象
    函数返回值：登录成功返回用户名
    '''
    print("-------------")
    print("| 1.用户注册 |")
    print("| 2.用户登录 |")
    print("| 3.校验名字 |")
    print("| 0.退出程序 |")   
    print("-------------")
    s = input("请输入功能序号：")
    if s == "1":
        error_code = user_reg(sock)
        if error_code:
            print("注册成功，赶快去登录吧！")
        else:
            print("注册失败！")
    elif s == "2":
        user_name = user_login(sock)
        if user_name:
            print("欢迎 %s 使用本文件传输工具！" % user_name)
            return user_name
        else:
            print("用户名或密码输入有误！")
        
    elif s == "3":
        error_code = check_name_existed(sock)
        if error_code == 1:
            print("校验通过，快去抢先注册吧！")
        else:
            print("该用户名已经被注册了哟！")

    elif s == "0":
        print("感谢你的使用，再见！")
        sys.exit()
    else:
        print("输入不合法！")


def main():
    while True:
        sock = socket.socket() # 创建套接字
        sock.connect((conf["app_server_ip"], conf["app_server_port"])) # 连接服务器

        user_name = menu(sock)  # 菜单函数
        if user_name:
            break

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

if __name__ == "__main__":
    main()



