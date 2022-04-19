#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2022/02/07 10:43
# @Author : 溪风习习
import os,sys
sys.path.append(os.getcwd())
import cx_Oracle as oracle
from common.log_util import logger
from common.yaml_util import read_config

DBtype = read_config("Project", "DBType")
DBInfo = read_config("OracleDB")

class OracleDB():
    if DBtype == "OracleDB":

        def __init__(self):

            dsn_oracle =  f'{DBInfo["host"]}:{DBInfo["post"]}/{DBInfo["service"]}'
            user_oracle = DBInfo["user"]
            password_oracle = DBInfo["password"]

            try:
                # 建立数据库连接
                self.conn = oracle.connect(
                    user = user_oracle,
                    password = password_oracle, 
                    dsn = dsn_oracle
                )
                # 使用 cursor 方法获取操作游标，得到一个可以执行sql语句，并且操作结果为字典返回的游标
                self.cur = self.conn.cursor()
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
    # a = OracleDB().query(sql = "select * from ORDER_INFO where ORDER_NO like 'YTJH-2203140004%'")
    # print(a)
    b = OracleDB().query(sql = "select ID, ORDER_TYPE from ORDER_INFO where ORDER_NO = 'YTJH-2203140004'")
    print(b)