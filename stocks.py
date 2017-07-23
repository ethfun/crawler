# -*- coding: UTF-8 -*-
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
import pymysql.cursors
import json
import time
import ast


# Connect to the database
connection = pymysql.connect(host='127.0.0.1',
                             user='test',
                             password='test',
                             db='test',
                             charset='utf8',
                             cursorclass=pymysql.cursors.DictCursor)

try:
    with connection.cursor() as cursor:
        # Read a single record
        sql = "SELECT `portfolio_id`, `portfolio_stocks`, `portfolio_type` FROM `portfolio`"
        cursor.execute(sql)
        sql_list = []
        # single_dict = {}
        for row in cursor:
            # print row['portfolio_stocks']
            # 根据格式转换为对应的类型
            # print type(ast.literal_eval(row['portfolio_stocks']))
            for stock in ast.literal_eval(row['portfolio_stocks']):
                # 检查是否为dict
                # print type(ast.literal_eval(stock))
                for key in ast.literal_eval(stock):
                    sql_list.append((key, str(row['portfolio_type']), row['portfolio_id'], ast.literal_eval(stock).get(key)))
                    # print key, ast.literal_eval(stock).get(key)
                # print str(ast.literal_eval(stock).keys())
        print sql_list

# Method one
# print row['portfolio_stocks'].replace('[', '').replace(']', '')
# Method Two 去除首尾
# print row['portfolio_stocks'].strip('[]')

        sql = "INSERT INTO `portfolio_detail` (`code`, `portfolio_type`, `portfolio_id`, `portfolio_amount`) VALUES (%s, %s, %s, %s)"
        cursor.executemany(sql, sql_list)
        connection.commit()

finally:
    connection.close()
