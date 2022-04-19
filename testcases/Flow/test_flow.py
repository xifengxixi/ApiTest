#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2022-04-19 15:30:28
# @Author : 溪风习习

import pytest
import allure
import time
from common.requests_util import RequestsUtil
from common.parameters_util import read_testcase

@allure.epic("吐哈接口测试")
@allure.feature("此处填写模块名称")
class TestFlow:

    @allure.story("此处填写接口名称")
    @pytest.mark.parametrize('caseinfo', read_testcase(r'\testcases\Flow\01_picture_yzm.yml'))
    def test_01_picture_yzm(self, caseinfo):
        allure.dynamic.title(caseinfo["name"])
        allure.dynamic.description(caseinfo["name"])
        RequestsUtil().analysis_yaml(caseinfo)

    @allure.story("此处填写接口名称")
    @pytest.mark.parametrize('caseinfo', read_testcase(r'\testcases\Flow\02_login.yml'))
    def test_02_login(self, caseinfo):
        allure.dynamic.title(caseinfo["name"])
        allure.dynamic.description(caseinfo["name"])
        RequestsUtil().analysis_yaml(caseinfo)

    @allure.story("此处填写接口名称")
    @pytest.mark.parametrize('caseinfo', read_testcase(r'\testcases\Flow\03_saveOrderByCar.yml'))
    def test_03_saveOrderByCar(self, caseinfo):
        allure.dynamic.title(caseinfo["name"])
        allure.dynamic.description(caseinfo["name"])
        RequestsUtil().analysis_yaml(caseinfo)

    @allure.story("此处填写接口名称")
    @pytest.mark.parametrize('caseinfo', read_testcase(r'\testcases\Flow\04_saveOrderByGoods.yml'))
    def test_04_saveOrderByGoods(self, caseinfo):
        allure.dynamic.title(caseinfo["name"])
        allure.dynamic.description(caseinfo["name"])
        RequestsUtil().analysis_yaml(caseinfo)

    @allure.story("此处填写接口名称")
    @pytest.mark.parametrize('caseinfo', read_testcase(r'\testcases\Flow\05_saveOrderByTotal.yml'))
    def test_05_saveOrderByTotal(self, caseinfo):
        allure.dynamic.title(caseinfo["name"])
        allure.dynamic.description(caseinfo["name"])
        RequestsUtil().analysis_yaml(caseinfo)

    @allure.story("此处填写接口名称")
    @pytest.mark.parametrize('caseinfo', read_testcase(r'\testcases\Flow\06_page_plan.yml'))
    def test_06_page_plan(self, caseinfo):
        allure.dynamic.title(caseinfo["name"])
        allure.dynamic.description(caseinfo["name"])
        RequestsUtil().analysis_yaml(caseinfo)

    @allure.story("此处填写接口名称")
    @pytest.mark.parametrize('caseinfo', read_testcase(r'\testcases\Flow\07_executionTasks.yml'))
    def test_07_executionTasks(self, caseinfo):
        allure.dynamic.title(caseinfo["name"])
        allure.dynamic.description(caseinfo["name"])
        RequestsUtil().analysis_yaml(caseinfo)

    @allure.story("此处填写接口名称")
    @pytest.mark.parametrize('caseinfo', read_testcase(r'\testcases\Flow\08_batchPass.yml'))
    def test_08_batchPass(self, caseinfo):
        allure.dynamic.title(caseinfo["name"])
        allure.dynamic.description(caseinfo["name"])
        RequestsUtil().analysis_yaml(caseinfo)

    @allure.story("此处填写接口名称")
    @pytest.mark.parametrize('caseinfo', read_testcase(r'\testcases\Flow\09_orderDetail.yml'))
    def test_09_orderDetail(self, caseinfo):
        allure.dynamic.title(caseinfo["name"])
        allure.dynamic.description(caseinfo["name"])
        RequestsUtil().analysis_yaml(caseinfo)

    @allure.story("此处填写接口名称")
    @pytest.mark.parametrize('caseinfo', read_testcase(r'\testcases\Flow\10_dispatch2carrierForCar.yml'))
    def test_10_dispatch2carrierForCar(self, caseinfo):
        allure.dynamic.title(caseinfo["name"])
        allure.dynamic.description(caseinfo["name"])
        RequestsUtil().analysis_yaml(caseinfo)

    @allure.story("此处填写接口名称")
    @pytest.mark.parametrize('caseinfo', read_testcase(r'\testcases\Flow\11_dispatch2carrierForGoods.yml'))
    def test_11_dispatch2carrierForGoods(self, caseinfo):
        allure.dynamic.title(caseinfo["name"])
        allure.dynamic.description(caseinfo["name"])
        RequestsUtil().analysis_yaml(caseinfo)

    @allure.story("此处填写接口名称")
    @pytest.mark.parametrize('caseinfo', read_testcase(r'\testcases\Flow\12_dispatch2carrierForTotal.yml'))
    def test_12_dispatch2carrierForTotal(self, caseinfo):
        allure.dynamic.title(caseinfo["name"])
        allure.dynamic.description(caseinfo["name"])
        RequestsUtil().analysis_yaml(caseinfo)

    @allure.story("此处填写接口名称")
    @pytest.mark.parametrize('caseinfo', read_testcase(r'\testcases\Flow\13_dispatch2CarForCar.yml'))
    def test_13_dispatch2CarForCar(self, caseinfo):
        allure.dynamic.title(caseinfo["name"])
        allure.dynamic.description(caseinfo["name"])
        RequestsUtil().analysis_yaml(caseinfo)