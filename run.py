import pytest
import time
import os
import traceback
from common.log_util import logger
from common.yaml_util import read_config

def run():
    # 从配置文件中获取项目名称
    ProjectName = read_config("Project", "ProjectName")
    try:
        logger.info(
            """
                         _    _         _      _____         _
              __ _ _ __ (_)  / \\  _   _| |_ __|_   _|__  ___| |_
             / _` | '_ \\| | / _ \\| | | | __/ _ \\| |/ _ \\/ __| __|
            | (_| | |_) | |/ ___ \\ |_| | || (_) | |  __/\\__ \\ |_
             \\__,_| .__/|_/_/   \\_\\__,_|\\__\\___/|_|\\___||___/\\__|
                  |_|
            开始执行{}项目...
            """.format(ProjectName)
        )
    except Exception:
        logger.error(f"运行异常:异常信息:{traceback.format_exc()}")
        raise Exception

if __name__ == '__main__':
    run()
    pytest.main()
    time.sleep(1)
    # os.system("allure generate ./reports/temps -o ./reports/report --clean")
    # os.system("allure serve ./reports/temps -p 9999")
