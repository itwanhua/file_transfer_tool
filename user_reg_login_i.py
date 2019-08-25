#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pymysql
import re
import getpass
import sys
import json



conf = json.load(open("server_conf.json")) # 配置信息


def check_user_name(user_name):
    '''
    函数功能：校验用户名
    函数参数：username 待校验的用户名
    返回值：用户名格式合法返回1，用户名格式不合法返回0，用户名已存在返回-1
    '''
    if not re.match("\w{6,15}$", user_name):
        return 0
    conn = pymysql.connect(conf["db_server"], conf["db_user"], conf["db_password"], conf["db_name"])  
    try:
        with conn.cursor() as cur:
            cur.execute("select uname from user where uname=%s", (user_name,))
            rows = cur.fetchone()
    finally:
        conn.close()
    if rows:
        return -1
    return 1


def check_user_passwd(user_passwd):
    '''
    函数功能：校验密码格式是否合法
    函数参数：user_passwd 待校验的用户密码
    返回值：密码格式合法返回1，密码格式不合法返回0
    '''
    if re.match("\w{6,15}$", user_passwd):
        return 1
    else:
        return 0


def check_uname_passwd(user_name, user_passwd):
    '''
    函数功能：校验密码是否匹配用户名
    函数参数：user_name 待校验的用户名, user_passwd 待校验的用户密码
    返回值：校验通过返回1，校验失败返回0
    '''
    conn = pymysql.connect(conf["db_server"], conf["db_user"], conf["db_password"], conf["db_name"])  
    try:
        with conn.cursor() as cur:
            cur.execute("select uname from user where uname=%s and passwd=%s", (user_name,user_passwd,))
            rows = cur.fetchone()
    finally:
        conn.close()
    if rows:
        return 1
    return 0



def check_user_phone(user_phone):
    '''
    函数功能：校验手机号格式是否合法
    函数参数：user_phone 待校验手机号
    返回值：校验通过返回1，校验失败返回0
    '''
    if re.match("^1\d{10}$", user_phone):
        return 1
    else:
        return 0


def check_user_email(user_email):
    '''
    函数功能：校验邮箱格式是否合法
    函数参数：user_email 待校验邮箱
    返回值：校验通过返回1，校验失败返回0
    '''
    if re.match("\w{0,19}@[0-9a-zA-Z]{1,13}\.com$", user_email):
        return 1
    else:
        return 0

def send_mss_code(user_phone):
    pass



# 注册时输入密码 
def input_user_passwd():
    print("规定密码只能包含英文字母、数字或下划线，长度6~15位")
    while True:
        user_passwd = getpass.getpass("请输入密码：")
        if check_user_passwd(user_passwd) == 1:
            user_passwd2 = getpass.getpass("请确认密码：")
            if user_passwd2 != user_passwd:     
                print("两次密码不匹配！")
                continue
            else:
                return user_passwd
        else:
            continue
# 注册时输入手机号
def input_user_phone():
    while True:
        user_phone = input("请输入手机号：")
        if check_user_phone() == 1:
            return user_phone
        else:
            print("手机号输入错误！")


# 注册成功将注册信息写入数据库
def commit_user(user_name, user_passwd, user_phone, user_email):
    conn = pymysql.connect(conf["db_server"], conf["db_user"], conf["db_password"], conf["db_name"])

    with conn.cursor() as cur:
        # sql = "insert into user (uname, passwd, phone, email) values (\"%s\", \"%s\", \"%s\", \"%s\")" %(user_name, user_passwd, user_phone, user_email)
        sql = "insert into user (uname, passwd, phone, email) values (%s, %s, %s, %s)" %(user_name, user_passwd, user_phone, user_email)
        cur.execute(sql)
        conn.commit()
        print("注册成功！\n")


def reg_main():
    '''
    函数功能：注册用户，输入信息包括用户名，密码，电话，邮箱
    函数返回值：注册成功返回 用户名
    '''
    # 输入用户名
    while True:
        user_name = input("请输入用户名（只能包含英文字母、数字或下划线，长度6~15位）：")
        if check_user_name(user_name) == 0:
            print("用户名格式错误！")
        elif check_user_name(user_name) == -1:
            print("用户名已存在！")
        else:
            break

    # 输入密码
    while True:
        user_passwd = getpass.getpass("请输入密码（只能包含英文字母、数字或下划线，长度6~15位）：")
        if check_user_passwd(user_passwd) == 1:           
            user_passwd2 = getpass.getpass("请确认密码：")
            if user_passwd2 == user_passwd: 
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


    # 将用户名，密码提交到数据库，注册成功
    commit_user(user_name, user_passwd, user_phone, user_email)

def login_main():
    '''
    函数功能：登录用户
    返回值：登录成功返回 用户名
    '''
    while True:
        while True:
            user_name = input("\n用户名>>")
            ret = check_user_name(user_name)

            if ret == -1:
                break
            else:
                print("用户名不存在，请重新输入！")

        while True:
            user_passwd = getpass.getpass("密码>>")
            ret = check_uname_passwd(user_name, user_passwd)
            if ret == 1:
                print("登录成功！")
                return user_name
            elif ret == 0:
                print("密码错误！")
                break

    
def user_center(user_name):
    print("\n%s，欢迎你使用本系统！" % user_name)
    print("-------------")
    print("| 1.盘点库存 |")
    print("| 2.查看销售 |")
    print("| 3.修改密码 |")
    print("| 0.退出用户 |")
    print("-------------")

    while True:
        op = input("\n请选择功能序号>>")
        if op == "0":
            print("感谢使用，下次再见！")
            sys.exit(2)
        elif op == "1":
            print("正在开发...")      
        elif op == "2":
            print("正在开发...")
        elif op == "3":
            print("正在开发...")


def main():
    print("----------")
    print("| 1.登录 |")
    print("| 2.注册 |")
    print("| 0.退出 |")
    print("----------")

    while True:
        op = input("\n请选择功能序号>>")
        if op == "0":
            print("感谢使用，下次再见！")
            sys.exit(2)
        elif op == "1":
            user_name= login_main()
            if user_name:
                user_center(user_name)              
        elif op == "2":
            reg_main()
            main()

   

if __name__ == "__main__":
    main()



