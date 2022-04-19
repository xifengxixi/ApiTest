import random
import datetime
from faker import Faker
from common.yaml_util import read_extract, read_config

class DebugTalk:

    def __init__(self):
        self.f = Faker(locale='zh_CN')

    def get_extract(self, node_name) -> str:
        """
        获取extract.yml文件中的值
        :return:
        """
        return read_extract(node_name)

    def get_url(self, node_name) -> str:
        """
        获取base_url
        :return:
        """
        return read_config('base', node_name)

    def get_random_number(self, min, max) -> int:
        """
        获取随机数
        :return:
        """
        return random.randint(int(min), int(max))

    def get_phone(self) -> int:
        """
        随机生成手机号码
        :return: 
        """
        phone = self.f.phone_number()
        return phone

    def get_id_number(self) -> int:
        """
        随机生成身份证号码
        :return:
        """
        id_number = self.f.ssn()
        return id_number

    def get_female_name(self) -> str:
        """
        女生姓名
        :return: 
        """
        female_name = self.f.name_male()
        return female_name

    def get_male_name(self) -> str:
        """
        男生姓名
        :return: 
        """
        male_name = self.f.name_female()
        return male_name

    def get_email(self) -> str:
        """
        生成邮箱
        :return: 
        """
        email = self.f.email()
        return email

    def get_time(self) -> datetime.datetime:
        """
        获取当前时间
        :return:
        """
        return datetime.datetime.now()

    def get_time_oneHourLater(self) -> datetime.datetime:
        """
        获取当前时间一小时后时间
        :return:
        """
        oneHourLater = (datetime.datetime.now()+ datetime.timedelta(hours=+1)).strftime("%Y-%m-%d %H:%M")
        return oneHourLater

    def get_time_oneDayLater(self) -> datetime.datetime:
        """
        获取当前时间一天后时间
        :return:
        """
        oneDayLater = (datetime.datetime.now()+ datetime.timedelta(days=+1)).strftime("%Y-%m-%d %H:%M")
        return oneDayLater