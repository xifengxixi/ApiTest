#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2022/03/18 15:04
# @Author : 溪风习习
import datetime
import os,sys
sys.path.append(os.getcwd())
from common.yaml_util import read_config

class AutomaticUtil:
    """自动生成自动化测试中的page代码"""

    # TODO 自动生成测试代码
    def __init__(self):
        pass

    def testcases_automatic(self):
        """ 自动生成 测试代码"""
        testcases_path = os.path.realpath(__file__).split('common')[0] + 'testcases\\'
        moduleName_list = os.listdir(testcases_path)
        ProjectName = read_config('Project', 'ProjectName')

        for module in moduleName_list:
            # 模块路径
            module_path = testcases_path + module + '\\'           
            # py文件名称
            casePath = module_path + 'test_' + module.lower() + '.py'
            # 类名称(获取模块的命名用于生成的类名称)
            classTitle = 'Test' + module.capitalize()
            # yaml路径名称list(用于生成yaml路径)
            yamlPath_list = []
            # yaml文件名称list(用于生成函数名称)
            yaml_list = []
            for root, dirs, files in os.walk(module_path):
                for file in files:
                    if '.yaml' in file or '.yml' in file:
                        yamlPath = '\\testcases' + '\\' + module + '\\' + file
                        yamlPath_list.append(yamlPath)
                        filePath = file.split('.')[0]
                        yaml_list.append('test_' + filePath)
            self.write_py(casePath, ProjectName, classTitle)
            if len(yaml_list):
                for i in range(0, len(yaml_list)):
                    self.write_py(casePath, ProjectName, classTitle, yaml_list[i], yamlPath_list[i])

    def write_py(self, casePath, ProjectName, classTitle, funcTitle=None, yamlPath=None):
        """
        自动生成py文件
        :param casePath: 生成的py文件地址
        :param ProjectName: 项目名称
        :param classTitle: 类名称,读取文件夹名称生成类名称
        :param funcTitle: 函数名称,读取yaml文件名称生成函数名称
        :param yamlPath: 用例文件路径
        :param caseDetail: 函数描述,读取用例中的描述内容,做为函数描述
        :return:
        """
        Author = read_config('Project', 'TestName')
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if funcTitle == None and yamlPath == None:
            write_mode = 'w'
            page = f'''#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : {now}
# @Author : {Author}

import pytest
import allure
import time
from common.requests_util import RequestsUtil
from common.parameters_util import read_testcase

@allure.epic("{ProjectName}")
@allure.feature("此处填写模块名称")
class {classTitle}:'''
        else:
            write_mode = 'a'
            page = f'''

    @allure.story("此处填写接口名称")
    @pytest.mark.parametrize('caseinfo', read_testcase(r'{yamlPath}'))
    def {funcTitle}(self, caseinfo):
        allure.dynamic.title(caseinfo["name"])
        allure.dynamic.description(caseinfo["name"])
        RequestsUtil().analysis_yaml(caseinfo)'''
        with open(casePath, mode=write_mode, encoding="utf-8") as f:
            f.write(page)

if __name__ == '__main__':
    AutomaticUtil().testcases_automatic()