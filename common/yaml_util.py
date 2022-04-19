import os
import yaml

def get_object_path():
    """
    获取项目根路径
    :return:
    """
    return os.path.realpath(__file__).split('common')[0]
    # return os.path.abspath(os.getcwd().split('common')[0])

def read_config(one_node, two_node=None):
    """
    读取config.yml文件
    :param one_node: 第一节点名
    :param two_node: 第二节点名
    :return:
    """
    with open(get_object_path()+'config.yml', encoding='utf-8') as f:
        value = yaml.load(stream=f, Loader=yaml.FullLoader)
        if two_node == None:
            return value[one_node]
        else:
            return value[one_node][two_node]

def read_extract(node_name):
    """
    读取extract.yml文件
    :param node_name: 节点名
    :return:
    """
    with open(get_object_path()+'extract.yml', encoding='utf-8') as f:
        value = yaml.load(stream=f, Loader=yaml.FullLoader)
        return value[node_name]

def write_extract(data):
    """
    写入extract.yml文件(以追加形式写入)
    :param data: 需要写入extract.yml的数据
    :return:
    """
    with open(get_object_path()+'extract.yml', encoding='utf-8', mode='a') as f:
        yaml.dump(data, stream=f, allow_unicode=True)

def clean_extract():
    """
    清空extract.yml文件
    :return:
    """
    with open(get_object_path()+'extract.yml', encoding='utf-8', mode='w') as f:
        f.truncate()

# # 读取yaml测试用例文件
# def read_testcase(yaml_path):
#     with open(get_object_path()+yaml_path, encoding='utf-8') as f:
#         value = yaml.load(stream=f, Loader=yaml.FullLoader)
#         return value