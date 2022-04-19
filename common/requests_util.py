import requests
import json
import jsonpath
import re
import ddddocr
import traceback
import datetime
import os,sys
sys.path.append(os.getcwd())
from common.parameters_util import read_testcase
from common.yaml_util import read_config,read_extract,write_extract
from debug_talk import DebugTalk
from common.log_util import logger
from common.oracle_util import OracleDB

class RequestsUtil:

    session = requests.session() # 获得session会话对象

    def __init__(self):
        self.last_headers = {}

    def do_replace(self, data):
        """
        热加载替换解析
        :param data: 处理yaml中需要热加载替换解析的数据
        :return:
        """
        try:
            # 不管什么类型统一转换成字符串格式
            if data and isinstance(data, dict):  # 若data不为空且data的类型为字典
                str_data = json.dumps(data)
            else:
                str_data = data
            # 替换值 热加载 ${}
            for i in range(1, str_data.count('${') + 1):
                if '${' in str_data:
                    if '}' in str_data:
                        start_index = str_data.index('${')
                        end_index = str_data.index('}', start_index)
                        old_value = str_data[start_index:end_index + 1]
                        # 若热加载的函数需要传参数
                        if '(' in str_data:
                            if ')' in str_data:
                                func_name = old_value[2:old_value.index('(')]
                                args_value = old_value[old_value.index('(') + 1:old_value.index(')')]
                                try:
                                    # 反射（通过一个函数的字符串直接去调用这个方法）
                                    new_value = getattr(DebugTalk(), func_name)(*args_value.split(','))
                                except AttributeError:
                                    logger.error("取值格式错误，请检查函数名！")
                                    raise AttributeError
                                except KeyError:
                                    logger.error("取值格式错误，请检查参数名！")
                                    raise KeyError
                            else:
                                logger.error("取值格式错误，请检查格式:${xx(xx)}!")
                                raise Exception("取值格式错误，请检查格式:${xx(xx)}!")
                        # 若热加载的函数不需要传参数
                        else:
                            func_name = old_value[old_value.index('{') + 1:old_value.index('}')]
                            try:
                                new_value = getattr(DebugTalk(), func_name)()
                            except AttributeError:
                                logger.error("取值格式错误，请检查函数名与格式${xx}!")
                                raise AttributeError
                        str_data = str_data.replace(old_value, str(new_value))
                    else:
                        logger.error("取值格式错误，请检查格式:${xx}!")
                        raise Exception("取值格式错误，请检查格式:${xx}!")
            # 替换值 {{}}
            for i in range(1, str_data.count('{{') + 1):
                if '{{' in str_data:
                    if '}}' in str_data:
                        start_index = str_data.index('{{')
                        end_index = str_data.index('}}', start_index)
                        old_value = str_data[start_index:end_index + 2]
                        new_value = read_extract(old_value[2:-2])
                        str_data = str_data.replace(old_value, new_value)
                    else:
                        logger.error("取值格式错误，请检查格式:{{xx}}!")
                        raise Exception("取值格式错误，请检查格式:{{xx}}!")
            # 还原数据类型
            if data and isinstance(data, dict):
                try:
                    data = json.loads(str_data)
                except json.decoder.JSONDecodeError:
                    logger.error("取值格式错误，请检查格式${xx}!")
                    raise  json.decoder.JSONDecodeError
            else:
                data = str_data
            return data
        except Exception:
            logger.error(f"热加载异常:异常信息:{traceback.format_exc()}")
            raise Exception

    def analysis_yaml(self, caseinfo):
        """
        规范功能测试yaml测试用例文件的写法,此方法中调用了发送请求方法
        :param caseinfo: 从yaml文件中读取得到的数据
        :return:
        """
        try:
            # 1、必须有的四个一级关键字：name、base_url、request、validate
            caseinfo_keys = dict(caseinfo).keys()
            if 'name' in caseinfo_keys and 'base_url' in caseinfo_keys and 'request' in caseinfo_keys and 'validate' in caseinfo_keys:
                base_url = caseinfo['base_url']
                self.base_url = self.do_replace(base_url)
                # 2、在request一级关键字下必须包含有两个二级关键字：method、url
                request_keys = dict(caseinfo['request']).keys()
                if 'method' in request_keys and 'url' in request_keys:
                    # 参数（params、data、json），请求头，文件上传等不能做约束
                    name = caseinfo['name']
                    method = caseinfo['request']['method']
                    del caseinfo['request']['method']
                    url = caseinfo['request']['url']
                    del caseinfo['request']['url']
                    headers = None
                    if jsonpath.jsonpath(caseinfo, '$..headers'):
                        headers = caseinfo['request']['headers']
                        del caseinfo['request']['headers']
                    files = None
                    if jsonpath.jsonpath(caseinfo, '$..files'):
                        files = caseinfo['request']['files']
                        for key, value in dict(files).items():
                            files[key] = open(value, 'rb')
                        del caseinfo['request']['files']
                    # 调用请求函数（把method、url、headers、files从caseinfo中去掉之后将剩下的传给kwargs）
                    res = self.do_requests(name=name, method=method, url=url, headers=headers, files=files,
                                            **caseinfo['request'])
                    return_text = res.text
                    status_code = res.status_code
                    yq_result = caseinfo['validate']
                    try:
                        return_data = res.json() # 前提是返回json格式，则获取res.json()                
                    except json.JSONDecodeError:
                        return_data = res.content # 若返回不是json格式，则获取res.content

                    # 提取接口关联的变量，支持正则表达式，支持json提取
                    self.do_extract(caseinfo, return_data, return_text)
                    # 调用数据库校验函数，先提取，后校验
                    self.do_dbCheck(caseinfo, return_data, query_type="all")
                    # 调用断言函数
                    self.do_validate(yq_result, return_data, status_code)
                else:
                    logger.error('2、在request一级关键字下必须包含有两个二级关键字:method、url')
                    raise Exception('2、在request一级关键字下必须包含有两个二级关键字:method、url')
            else:
                logger.error('1、必须有的四个一级关键字:name、base_url、request、validate')
                raise Exception('1、必须有的四个一级关键字:name、base_url、request、validate')
        except Exception:
            logger.error(f"分析yaml文件异常:异常信息:{traceback.format_exc()}")
            raise Exception

    def do_requests(self, name, method, url, headers=None, file=None, **kwargs):
        """
        统一请求的方法
        :param name: yaml中自定义的接口名称
        :param method: 请求方法
        :param url: 请求路径
        :param headers: 请求头
        :param file: 文件上传
        :param kwargs: 可变参数
        :return:
        """
        try:
            # 处理method
            self.last_method = str(method).lower()
            # 处理基础路径
            self.last_url = self.base_url + self.do_replace(url)
            # 处理请求头
            if headers and isinstance(headers, dict):
                self.last_headers = self.do_replace(headers)
            # 最核心的地方：请求数据如何去替换：可能是params，data，json
            for key, value in kwargs.items():
                if key in ['params', 'data', 'json']:
                    kwargs[key] = self.do_replace(value)
            # 收集日志
            logger.info("----------接口请求开始----------")
            logger.info(f"接口名称：{name}")
            logger.info(f"请求方式：{self.last_method}")
            logger.info(f"请求路径：{self.last_url}")
            logger.info(f"请求头：{self.last_headers}")
            if 'params' in kwargs.keys():
                logger.info(f"请求参数：{kwargs['params']}")
            elif 'data' in kwargs.keys():
                logger.info(f"请求参数：{kwargs['data']}")
            elif 'json' in kwargs.keys():
                logger.info(f"请求参数：{kwargs['json']}")
            logger.info(f"文件上传：{file}")
            # 发送请求
            res = RequestsUtil.session.request(method=self.last_method, url=self.last_url, headers=self.last_headers, **kwargs)
            return res
        except Exception:
            logger.error(f"发送请求异常:异常信息:{traceback.format_exc()}")
            raise Exception

    def do_extract(self, caseinfo, return_data, return_text):
        """
        提取封装函数
        :param caseinfo: 用例数据,经过analysis_yaml函数对yaml文件数据进行分析之后的字典格式数据
        :param return_text: 接口返回的res.text
        :param return_data: 若接口返回存在res.json(),则返回res.json():若不存在res.json(),则返回res.content
        :return:
        """
        try:
            caseinfo_keys = dict(caseinfo).keys()
            if 'extract' in caseinfo_keys:
                if caseinfo['extract']:
                    # 计算extract中提取值重复次数,并按次数顺序取值
                    dict_count = {}
                    for key, value in dict(caseinfo['extract']).items():
                        # 正则提取
                        if '(.+?)' in value or '(.*?)' in value:
                            if re.search('"(.*?)"',value):
                                regular_key = re.search('"(.*?)"',value).group(1)
                            elif re.search("'(.+?)'",value):
                                regular_key = re.search("'(.+?)'",value).group(1)
                            if re.search(value, return_text):
                                # 若提取的元素没有重复
                                if regular_key not in dict_count.keys():
                                    dict_count[regular_key] = 1
                                    regular_value = re.search(value, return_text)
                                    extract_data = {key: regular_value.group(1)}
                                # 若提取的元素有重复
                                else:
                                    dict_count[regular_key] = dict_count[regular_key] + 1
                                    j = dict_count[regular_key] # j代表提取元素重复的次数
                                    regular_value = re.compile(value).findall(return_text)
                                    extract_data = {key: regular_value[j-1]}
                                write_extract(extract_data)
                            else:
                                logger.info(f"实际结果：{return_text}")
                                logger.error("未找到对应提取数据,请检查一级关键字extract中正则表达式格式")
                                raise Exception("未找到对应提取数据,请检查一级关键字extract中正则表达式格式")
                        # 图片验证码提取，此提取方式适用于图片验证码接口获取res.content
                        elif value == '${get_image_code}':
                            ddddocr_value = ddddocr.DdddOcr().classification(return_data)
                            extract_data = {key: ddddocr_value}
                            write_extract(extract_data)
                        # jsonpath提取
                        elif '$.' in value:
                            if jsonpath.jsonpath(return_data, value):
                                jsonpath_data = jsonpath.jsonpath(return_data, value)[0]
                                extract_data = {key: jsonpath_data}
                                write_extract(extract_data)
                            else:
                                logger.error("未找到对应提取数据,请检查一级关键字extract中jsonpath提取格式")
                                raise Exception("未找到对应提取数据,请检查一级关键字extract中jsonpath提取格式")
                        # json提取
                        else:
                            if jsonpath.jsonpath(return_data, f'$..{value}'):
                                json_value = jsonpath.jsonpath(return_data, f'$..{value}')
                                # 若提取的元素没有重复
                                if value not in dict_count.keys():
                                    dict_count[value] = 1
                                    extract_data = {key: json_value[0]}
                                # 若提取的元素有重复
                                else:
                                    dict_count[value] = dict_count[value] + 1
                                    j = dict_count[value]
                                    extract_data = {key: json_value[j-1]}
                                write_extract(extract_data)
                            else:
                                logger.info(f"实际结果：{return_text}")
                                logger.error("未找到对应提取数据,请检查一级关键字extract中json提取格式")
                                raise Exception("未找到对应提取数据,请检查一级关键字extract中json提取格式")
        except Exception:
            logger.error(f"提取结果异常:异常信息:{traceback.format_exc()}")
            raise Exception

    def do_validate(self, yq_result, sj_result, status_code):
        """
        断言封装函数
        :param yq_result: 预期结果
        :param sj_result: 实际结果
        :param status_code: 实际状态码
        """
        try:
            # 收集日志
            logger.info(f"预期结果：{yq_result}")
            logger.info(f"实际结果：{sj_result}")
            # 设置断言是否成功的标记，0代表断言成功，否则失败
            flag = 0
            if yq_result and isinstance(yq_result, list):
                for yq in yq_result:
                    for key, value in dict(yq).items():
                        # 判断断言方式
                        if key == 'equals':
                            for assert_key, assert_value in dict(value).items():
                                if assert_key == 'status_code':
                                    if assert_value != status_code:
                                        flag = flag + 1
                                        logger.error(f"断言equals失败;{assert_key}预期结果:{assert_value}不等于实际结果:{status_code}")
                                        raise Exception(f"断言equals失败;{assert_key}预期结果:{assert_value}不等于实际结果:{status_code}")
                                else:
                                    sj_value_list = jsonpath.jsonpath(sj_result, f'$..{assert_key}')
                                    if sj_value_list:
                                        if assert_value not in sj_value_list:
                                            flag = flag + 1
                                            logger.error(f"断言equals失败;{assert_key}预期结果:{assert_value}不等于实际结果:{sj_value_list[0]}")
                                            raise Exception(f"断言equals失败;{assert_key}预期结果:{assert_value}不等于实际结果:{sj_value_list[0]}")
                                    else:
                                        flag = flag + 1
                                        logger.error(f"断言equals失败;实际结果中不存在{assert_key}")
                                        raise Exception(f"断言equals失败;实际结果中不存在{assert_key}")
                        elif key == 'contains':
                            if not jsonpath.jsonpath(sj_result, f'$..{value}'):
                                flag = flag + 1
                                logger.error(f"断言contains失败;实际结果中不包含{value}")
                                raise Exception(f"断言contains失败;实际结果中不包含{value}")
                        else:
                            flag = flag + 1
                            logger.error(f"暂不支持此断言方式：{key}，请联系管理员！")
                            raise Exception(f"暂不支持此断言方式：{key}，请联系管理员！")
            # 断言处理
            assert flag == 0
            logger.info("接口请求成功")
            logger.info("----------接口请求结束----------\n")
        except Exception:
            logger.info("接口请求失败")
            logger.info("----------接口请求结束----------\n")
            logger.error(f"断言异常:异常信息:{traceback.format_exc()}")
            raise Exception(f"断言异常:异常信息:{traceback.format_exc()}")

    def do_dbCheck(self, caseinfo, return_data, query_type="all"):
        """
        数据库校验
        :param caseinfo: 用例数据,经过analysis_yaml函数对yaml文件数据进行分析之后的字典格式数据
        :param return_data: 接口返回数据,字典格式
        :param query_type: 数据库查询方式,默认为"all"查询全部,"one"查询单条
        :return:
        """
        try:
            caseinfo_keys = dict(caseinfo).keys()
            if 'db' in caseinfo_keys:
                if caseinfo['db']:
                    # 若sql不为空且接口返回结果为字典格式
                    if caseinfo['db']['sql'] and isinstance(return_data, dict):
                        sql_db = caseinfo['db']['sql']
                        query_data = self.db_query(sql_db, return_data, query_type)
                        # sql查询后对需要数据进行提取
                        if caseinfo['db']['dbextract']:
                            extract_db = caseinfo['db']['dbextract']
                            for key, value in dict(extract_db).items():
                                dbextract_value = eval(str(query_data)+value)
                                extract_data = {key: dbextract_value}
                                write_extract(extract_data)
                        # sql查询后进行数据库校验
                        if caseinfo['db']['jsonpath'] and caseinfo['db']['type'] and caseinfo['db']['value']:
                            jsonpath_db = caseinfo['db']['jsonpath']
                            type_db = caseinfo['db']['type']
                            value_db = caseinfo['db']['value']
                            if len(jsonpath_db) == len(type_db) == len(value_db):
                                # 通过循环逐一进行数据库校验
                                for i in range(0, len(jsonpath_db)):
                                    if jsonpath.jsonpath(return_data, jsonpath_db[i]):
                                        jsonpath_data = jsonpath.jsonpath(return_data, jsonpath_db[i])[0]
                                        value_data = eval(str(query_data)+value_db[i])
                                        type_data = type_db[i]
                                        if type_data == '==':
                                            try:
                                                assert jsonpath_data == value_data
                                            except Exception:
                                                logger.error(f"数据库校验'=='失败;数据库查询结果:{value_data} != 返回结果:{jsonpath_data}")
                                                raise Exception
                                        elif str(type_data).lower() == 'in':
                                            try:
                                                assert str(value_data) in str(jsonpath_data)
                                            except Exception:
                                                logger.error(f"数据库校验'in'失败;数据库查询结果:{value_data} not in 返回结果:{jsonpath_data}")
                                                raise Exception
                                        else:
                                            logger.error(f"数据库校验暂不支持此断言方式：{type_data}，请联系管理员！")
                                            raise Exception(f"数据库校验暂不支持此断言方式：{type_data}，请联系管理员！")
                                    else:
                                        logger.error(f"返回结果中不存在jsonpath:{jsonpath_db[i]}，请检查！")
                                        raise Exception(f"返回结果中不存在jsonpath:{jsonpath_db[i]}，请检查！")
                            else:
                                logger.error("数据库校验jsonpath、type、value组数不一致,请检查!")
        except Exception:
            logger.error(f"数据库校验异常:异常信息:{traceback.format_exc()}")
            raise Exception

    def db_query(self, sql: list, resp=None, query_type="all"):
        """
        执行 sql, 负责处理 yaml 文件中的断言需要执行多条 sql 的场景，最终会将所有数据以对象形式返回
        :param sql: sql
        :param resp: 接口响应数据，字典格式
        :param query_type: 数据库查询方式，默认为"all"查询全部，"one"查询单条
        :return:
        """
        DBtype = read_config("Project", "DBType")
        try:
            if isinstance(sql, list):
                data = []
                if 'UPDATE' and 'update' and 'DELETE' and 'delete' and 'INSERT' and 'insert' in sql:
                    raise "数据库校验的的sql必须是查询的sql"
                else:
                    for sql_row in sql:
                        # 判断sql中是否有正则替换内容，如果有则通过jsonpath提取相关的数据
                        sql = self.sql_replace(sql_row, resp)
                        # for 循环逐条处理断言 sql，并将sql 返回的所有内容全部放入对象中(字典列表的格式)
                        # 此处调用配置文件config.yml中对应数据库的查询函数，因此需要导入对应数据库工具的类
                        query_data = eval(DBtype)().query(sql, query_type)
                        for i in query_data:
                            data.append(i)
                    return data
            else:
                raise "数据库校验的查询sql需要是list类型"
        except Exception:
            logger.error(f"数据库db_query异常:异常原因:{traceback.format_exc()}")
            raise Exception
    
    def sql_replace(self, value, res=None):
        """
        sql替换:这里处理sql中的依赖数据,通过jsonpath的方式获取接口响应的值进行替换
        :param res: jsonpath使用的返回结果,字典格式
        :param value:
        :return:
        """
        try:
            SqlJsonList = re.findall(r"\$json\{(.*?)\}", value)
            for i in SqlJsonList:
                pattern = re.compile(r'\$json\{' + i.replace('$', "\$").replace('[', '\[') + r'\}')
                key = str(jsonpath.jsonpath(res, i)[0])
                value = re.sub(pattern, key, value, count=1)
                value = self.sql_replace(value, res)
            return value
        except Exception:
            logger.error(f"sql替换异常:异常原因:{traceback.format_exc()}")

if __name__ == '__main__':
    pass
