import csv
import json
import jsonpath
import yaml
import re
import traceback
import os,sys
sys.path.append(os.getcwd())
from common.yaml_util import get_object_path
from common.log_util import logger

def read_csv(csv_path):
    """
    读取csv数据文件
    :param csv_path: csv文件路径
    :return: 
    """
    try:
        csv_data_list = []
        with open(get_object_path()+csv_path, encoding='utf-8') as f:
            csv_data = csv.reader(f)
            for row in csv_data:
                csv_data_list.append(row)
        return csv_data_list
    except Exception:
        logger.error(f"读取csv数据文件异常:异常信息:{traceback.format_exc()}")
        raise Exception

def read_testcase(yaml_path):
    """
    读取yaml测试用例文件
    :param yaml_path: yaml测试用例文件路径
    :return:
    """
    try:
        with open(get_object_path()+yaml_path, encoding='utf-8') as f:
            caseinfo = yaml.load(stream=f, Loader=yaml.FullLoader)
            caseinfo_keys = dict(*caseinfo).keys()
            # 支持原生参数化
            if len(caseinfo) >= 2:
                return caseinfo
            else:
                if 'parameters' in caseinfo_keys:
                    parameters_data = jsonpath.jsonpath(caseinfo, '$..parameters')
                    # 支持csv参数化
                    if parameters_data != [None]:
                        new_caseinfo = analysis_parameters(*caseinfo)
                        return new_caseinfo
                    else:
                        return caseinfo
                else:
                    return caseinfo
    except Exception:
        logger.error(f"读取yaml用例文件异常:异常信息:{traceback.format_exc()}")
        raise Exception

def analysis_parameters(caseinfo:dict) -> list:
    """
    分析参数化
    :param caseinfo: 用例数据，字典格式
    :return: 若未参数化，返回字典格式；若参数化，则返回字典列表
    """
    try:
        caseinfo_keys = dict(caseinfo).keys()
        if 'parameters' in caseinfo_keys:
            if caseinfo['parameters'] != [None]:
                for key, value in dict(caseinfo['parameters']).items():
                    caseinfo_str = json.dumps(caseinfo)
                    key_list = str(key).split('-')
                    # 规范csv数据的写法
                    flag_form = True
                    csv_data_list = read_csv(value)
                    first_row = csv_data_list[0]
                    for parameters_key in key_list:
                        if parameters_key not in first_row:
                            flag_form = False
                            logger.error("yaml文件parameters中部分key不存在于csv中,请检查!")
                            raise Exception("yaml文件parameters中部分key不存在于csv中,请检查!")
                    for row in csv_data_list:
                        if len(row) != len(first_row):
                            flag_form = False
                            logger.error("csv文件各行长度间存在不一致,请检查!")
                            raise Exception("csv文件各行长度间存在不一致,请检查!")
                    # 解析
                    new_caseinfo = []
                    if flag_form:
                        for x in range(1, len(csv_data_list)):
                            temp_caseinfo = caseinfo_str
                            for y in range(0, len(csv_data_list[x])):
                                if csv_data_list[0][y] in key_list:
                                    if csv_data_list[0][y] in temp_caseinfo:
                                        old_value = "$csv{"+csv_data_list[0][y]+"}"
                                        if csv_data_list[0][y] in ['extract', 'dbextract']:
                                            # 调用change_extract函数替换extract特殊字符串格式为字典格式,特殊字符串格式不能通过json.loads转换
                                            new_value = json.dumps(replace_extract(csv_data_list[x][y]))
                                            temp_caseinfo = temp_caseinfo.replace(old_value, new_value)
                                            # 将'extract'替换之后，会变成字符串格式多出双引号，此处去除将其变为字典格式，以便后续json.loads转换，否则格式出错
                                            temp_caseinfo = temp_caseinfo.replace('"'+new_value+'"', new_value)
                                        elif csv_data_list[0][y] in ['jsonpath', 'type', 'value', 'sql']:
                                            new_value = json.dumps(replace_db(csv_data_list[x][y]))
                                            temp_caseinfo = temp_caseinfo.replace(old_value, new_value)
                                            temp_caseinfo = temp_caseinfo.replace('"'+new_value+'"', new_value)
                                        elif csv_data_list[0][y] == 'validate':
                                            new_value = json.dumps(replace_validate(csv_data_list[x][y]))
                                            temp_caseinfo = temp_caseinfo.replace(old_value, new_value)
                                            temp_caseinfo = temp_caseinfo.replace('"'+new_value+'"', new_value)
                                        else:
                                            if '-' in csv_data_list[x][y]:
                                                csv_data_list[x][y] = csv_data_list[x][y].replace('-', ',')
                                            try:
                                                new_value_eval = eval(csv_data_list[x][y])
                                                if isinstance(new_value_eval, str):
                                                    temp_caseinfo = temp_caseinfo.replace(old_value, new_value_eval)
                                                else:
                                                    new_value = json.dumps(new_value_eval)
                                                    temp_caseinfo = temp_caseinfo.replace(old_value, new_value)
                                                    temp_caseinfo = temp_caseinfo.replace('"'+new_value+'"', new_value)
                                            except:
                                                new_value = csv_data_list[x][y]
                                                temp_caseinfo = temp_caseinfo.replace(old_value, new_value)
                                    else:
                                        logger.error(f"yaml用例文件中不存在参数化关键字:{csv_data_list[0][y]}，请检查!")
                                        raise Exception(f"yaml用例文件中不存在参数化关键字:{csv_data_list[0][y]}，请检查!")
                            temp_caseinfo = json.loads(temp_caseinfo)
                            new_caseinfo.append(temp_caseinfo)
                    return new_caseinfo
            else:
                return caseinfo # 若yaml用例中存在parameters关键字但为空
        else:
            return caseinfo # 若yaml用例中不存在parameters关键字
    except Exception:
        logger.error(f"分析parameters参数异常:异常信息:{traceback.format_exc()}")
        raise Exception

def replace_extract(extract_str:str) -> dict:
    """
    替换extract特殊字符串格式为字典
    :param extract_str: extract自定义特殊字符串格式
    :return: 字典格式
    """
    try:
        extract_data = {}
        extract_list = extract_str.split('-')
        for extract_unit in extract_list:
            if '(.+?)' in extract_unit or '(.*?)' in extract_unit:
                extract_key = extract_unit.split(':', 1)[0]
                extract_value = extract_unit.split(':', 1)[1]
                extract_data[extract_key] = eval(extract_value)
            else:
                extract_key = extract_unit.split(':')[0]
                extract_value = extract_unit.split(':')[1]
                extract_data[extract_key] = extract_value
        return extract_data
    except Exception:
        logger.error(f"替换extract异常:异常信息:{traceback.format_exc()}")
        raise Exception

def replace_db(db_str:str) -> list:
    """
    替换db特殊字符串格式为列表
    :param db_str: db自定义特殊字符串格式
    :return: 列表格式
    """
    try:
        db_list = db_str.split('-')
        return db_list
    except Exception:
        logger.error(f"替换db异常:异常信息:{traceback.format_exc()}")
        raise Exception

def replace_validate(validate_str:str) -> list:
    """
    替换validate特殊字符串格式为列表
    :param validate_str: validate自定义特殊字符串格式
    :return: 列表格式
    """
    try:
        validate_data = []
        validate_list = validate_str.split('-')
        for validate_unit in validate_list:
            validate_key = validate_unit.split(':',1)[0]
            validate_value = validate_unit.split(':',1)[1]
            validate_dict = {}
            if validate_key == 'equals':
                list = re.split('{|:|}', validate_value)
                key = list[1]
                value = list[2]
                equals_dict = {}
                try:
                    equals_dict[key] = eval(value)
                    validate_dict[validate_key] = equals_dict
                    validate_data.append(validate_dict)
                except NameError:
                    equals_dict[key] = value
                    validate_dict[validate_key] = equals_dict
                    validate_data.append(validate_dict)
            elif validate_key == 'contains':
                validate_dict[validate_key] = validate_value
                validate_data.append(validate_dict)
        return validate_data
    except Exception:
        logger.error(f"替换validate异常:异常信息:{traceback.format_exc()}")
        raise Exception