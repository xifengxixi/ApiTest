import pytest
import socket
from common.dingtalk_util import DingTalk
from common.log_util import logger
from common.yaml_util import clean_extract, read_config

ProjectName = read_config('Project', 'ProjectName')
TestName = read_config('Project', 'TestName')
NotificationType = read_config('Project', 'NotificationType')
Environment = read_config('Project', 'Environment')
DingTalkSendType = read_config('DingTalk', 'send_type')
DingTalkMobiles = read_config('DingTalk', 'mobiles')

@pytest.fixture(scope='session', autouse=True)
def auto_clean_extract():
    clean_extract()

# 此函数名由pytest提供,不可随意更改
def pytest_terminal_summary(terminalreporter):
    """
    收集并统计用例结果
    :param terminalreporter: 内部使用的终端测试报告对象
    :return:
    """
    try:
        totalNum = terminalreporter._numcollected
        passNum = len([i for i in terminalreporter.stats.get('passed', []) if i.when != 'teardown'])
        failNum = len([i for i in terminalreporter.stats.get('failed', []) if i.when != 'teardown'])
        errorNum = len([i for i in terminalreporter.stats.get('error', []) if i.when != 'teardown'])
        skipNum = len([i for i in terminalreporter.stats.get('skipped', []) if i.when != 'teardown'])
        passRate = '成功率：%.2f' % (
            len(terminalreporter.stats.get('passed', [])) / terminalreporter._numcollected * 100) + '%'

        # logger.info(terminalreporter.stats)
        logger.warning("==========用例结果统计==========")
        logger.info("执行用例总数: {}".format(totalNum))
        logger.info("执行通过用例数:{}".format(passNum))
        logger.error("执行失败用例数:{}".format(failNum))
        logger.info("执行异常用例数:{}".format(errorNum))
        logger.info("执行跳过用例数:{}".format(skipNum))
        logger.info('执行成功率: {}'.format(passRate))
        logger.warning("==========用例结果统计==========")

        # # TODO 完善失败用例负责人，用例执行失败@对应的负责人
        if NotificationType == 0:
            pass
        elif NotificationType == 1:
            # 发送钉钉通知
            sendDingNotification(totalNum, passNum, failNum, errorNum, skipNum, passRate)
        # elif NotificationType == 2:
        #     # 发送企业微信通知
        #     sendEmailNotification(passNum, failNum, errorNum, skipNum, passRate)
        else:
            raise "NotificationType配置不正确，现在只支持企业微信通知和邮箱通知"

    except ZeroDivisionError:
        raise "程序中未发现可执行测试用例，请检查是否创建测试用例或者用例是否以test开头"

def sendDingNotification(totalNum: int, passNum: int, failNum: int,
                         errorNum: int, skipNum: int, passRate):
    # 发送钉钉通知
    text = f"#### {ProjectName}自动化通知 \n\n" \
           f">Python脚本任务: {ProjectName} \n\n" \
           f">环境: {Environment} \n\n" \
           f">执行人: {TestName} \n\n" \
           f">执行结果: {passRate} \n\n" \
           f">总用例数: {totalNum} \n\n" \
           f">成功用例数: {passNum} \n\n" \
           f">失败用例数: {failNum} \n\n" \
           f">异常用例数: {errorNum} \n\n" \
           f">跳过用例数: {skipNum} \n\n" \
           f"![screenshot](http://www.timesnew.cn/static/img/banner1.9e4ceb4.png)\n\n" \
           f"> ###### 测试报告 [详情](http://{get_host_ip()}:9999/index.html) \n\n"
    eval(f"DingTalk().send_{DingTalkSendType}")(
        title = f"【{ProjectName}自动化通知】",
        msg = text,
        mobiles = DingTalkMobiles
    )

def get_host_ip() -> str:
    """
    查询本机ip地址
    :return:
    """
    global s
    try:
        s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        s.connect(('8.8.8.8',80))
        ip = s.getsockname()[0]
    finally:
        s.close()

    return ip

# def sendEmailNotification(passNum: int, failNum: int,
#                           errorNum: int, skipNum: int, passRate):
#     # 发送企业微信通知
#     text = """【{0}自动化通知】
#                                 >测试环境：<font color=\"info\">TEST</font>
#                                 >测试负责人：@{1}
#                                 >
#                                 > **执行结果**
#                                 ><font color=\"info\">{2}</font>
#                                 >成功用例数：<font color=\"info\">{3}</font>
#                                 >失败用例数：`{4}个`
#                                 >异常用例数：`{5}个`
#                                 >跳过用例数：<font color=\"warning\">{6}个</font>
#                                 >时　间：<font color=\"comment\">{7}</font>
#                                 >
#                                 >非相关负责人员可忽略此消息。
#                                 >测试报告，点击查看>>[测试报告入口](http://121.43.35.47/:9999/index.html)""" \
#         .format(_PROJECT_NAME, _TEST_NAME, passRate, passNum, failNum, errorNum, skipNum, NowTime())
#
#     WeChatSend().sendMarkdownMsg(text)


