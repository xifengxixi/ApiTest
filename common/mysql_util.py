#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2022/02/07 10:43
# @Author : 溪风习习
import pymysql
import os,sys
sys.path.append(os.getcwd())
from warnings import filterwarnings
from common.log_util import logger
from common.yaml_util import read_config

# 忽略 Mysql 告警信息
filterwarnings("ignore", category=pymysql.Warning)

DBtype = read_config("Project", "DBType")
DBInfo = read_config("MysqlDB")

class MysqlDB():
    if DBtype == "MysqlDB":

        def __init__(self):
            
            host_mysql = DBInfo["host"]
            user_mysql = DBInfo["user"]
            password_mysql = DBInfo["password"]
            db_mysql = DBInfo["db"]

            try:
                # 建立数据库连接
                self.conn = pymysql.connect(
                    host = host_mysql,
                    user = user_mysql,
                    password = password_mysql,
                    db = db_mysql
                )

                # 使用 cursor 方法获取操作游标，得到一个可以执行sql语句，并且操作结果为字典返回的游标
                self.cur = self.conn.cursor(cursor=pymysql.cursors.DictCursor)
            except Exception as e:
                logger.error("数据库连接失败，失败原因{0}".format(e))

        def __del__(self):
            try:
                # 关闭游标
                self.cur.close()
                # 关闭连接
                self.conn.close()
            except Exception as e:
                logger.error("数据库关闭失败，失败原因{0}".format(e))

        def query(self, sql, state="all"):
            """
                查询
                :param sql:
                :param state:  all 是默认查询全部
                :return:
                """
            try:
                self.cur.execute(sql)
                # 获取数据库表的第一行即字段名
                columns = [col[0] for col in self.cur.description]
                if state.lower() == "all":
                    # 查询全部，并将查询内容以字典列表的形式返回
                    return [
                        dict(zip(columns, row))
                        for row in self.cur.fetchall()
                    ]
                else:
                    # 查询单条，并将查询内容以字典列表的形式返回
                    return [
                        dict(zip(columns, self.cur.fetchone()))
                    ]
            except Exception as e:
                logger.error("数据库查询失败，失败原因{0}".format(e))

        def execute(self, sql):
            """
                更新 、 删除、 新增
                :param sql:
                :return:
                """
            try:
                # 使用 excute 操作 sql
                rows = self.cur.execute(sql)
                # 提交事务
                self.conn.commit()
                return rows
            except Exception as e:
                logger.error("数据库操作失败，失败原因{0}".format(e))
                # 如果事务异常，则回滚数据
                self.conn.rollback()

if __name__ == '__main__':
    a = MysqlDB().query(sql = "select * from ORDER_INFO where ORDER_NO like 'YTJH-2203140004%'")
    print(a)