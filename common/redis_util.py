from rediscluster import RedisCluster
from typing import Optional, Union, List, Dict, Set


class RedisClient:
    def __init__(self, startup_nodes: List[Dict[str, Union[str, int]]], password: Optional[str] = None):
        """
        初始化 Redis 集群连接
        :param startup_nodes: Redis 集群的启动节点列表（至少提供一个），格式：[{"host": "xx", "port": 6379}]
        :param password: Redis 认证密码（如果有）
        """
        self.client = RedisCluster(startup_nodes=startup_nodes, decode_responses=True, password=password,
                                   skip_full_coverage_check=True)

    def __del__(self):
        """
        析构函数：对象销毁时自动关闭 Redis 连接
        """
        if hasattr(self, "client"):
            self.client.close()

    # ---- 字符串（String）操作 ----
    def set(self, key: str, value: Union[str, int, float], expire: Optional[int] = None) -> bool:
        """
        设置键值对
        :param key: 键名
        :param value: 存储的值（字符串、整数或浮点数）
        :param expire: 过期时间（秒），如果为 None，则不过期
        :return: 是否成功设置（True/False）
        """
        return self.client.set(key, value, ex=expire)

    def get(self, key: str) -> Optional[str]:
        """
        获取存储的值
        :param key: 键名
        :return: 存储的值（字符串），如果键不存在则返回 None
        """
        return self.client.get(key)

    def delete(self, key: str) -> bool:
        """
        删除指定的键
        :param key: 要删除的键名
        :return: 是否删除成功（True/False）
        """
        return self.client.delete(key) > 0

    def exists(self, key: str) -> bool:
        """
        判断键是否存在
        :param key: 键名
        :return: 是否存在（True/False）
        """
        return self.client.exists(key) > 0

    def incr(self, key: str, amount: int = 1) -> int:
        """
        递增键的值
        :param key: 键名
        :param amount: 递增的步长（默认为1）
        :return: 递增后的值
        """
        return self.client.incr(key, amount)

    def decr(self, key: str, amount: int = 1) -> int:
        """
        递减键的值
        :param key: 键名
        :param amount: 递减的步长（默认为1）
        :return: 递减后的值
        """
        return self.client.decr(key, amount)

    # ---- 哈希表（Hash）操作 ----
    def hset(self, name: str, key: str, value: str) -> bool:
        """
        设置哈希表字段的值
        :param name: 哈希表名称
        :param key: 字段名
        :param value: 存储的值
        :return: 是否成功设置（True/False）
        """
        return self.client.hset(name, key, value)

    def hget(self, name: str, key: str) -> Optional[str]:
        """
        获取哈希表字段的值
        :param name: 哈希表名称
        :param key: 字段名
        :return: 存储的值，如果键不存在则返回 None
        """
        return self.client.hget(name, key)

    def hdel(self, name: str, key: str) -> bool:
        """
        删除哈希表中的字段
        :param name: 哈希表名称
        :param key: 要删除的字段名
        :return: 是否删除成功（True/False）
        """
        return self.client.hdel(name, key) > 0

    def hkeys(self, name: str) -> List[str]:
        """
        获取哈希表中的所有字段名
        :param name: 哈希表名称
        :return: 字段名列表
        """
        return self.client.hkeys(name)

    def hvals(self, name: str) -> List[str]:
        """
        获取哈希表中的所有值
        :param name: 哈希表名称
        :return: 值的列表
        """
        return self.client.hvals(name)

    # ---- 列表（List）操作 ----
    def lpush(self, key: str, *values: str) -> int:
        """
        从左侧向列表中插入值
        :param key: 列表名称
        :param values: 要插入的值（可多个）
        :return: 插入后列表的长度
        """
        return self.client.lpush(key, *values)

    def rpop(self, key: str) -> Optional[str]:
        """
        从右侧弹出列表中的值
        :param key: 列表名称
        :return: 弹出的值，如果列表为空则返回 None
        """
        return self.client.rpop(key)

    def lrange(self, key: str, start: int = 0, end: int = -1) -> List[str]:
        """
        获取列表中指定范围的值
        :param key: 列表名称
        :param start: 开始索引（默认为0）
        :param end: 结束索引（默认为-1，即所有）
        :return: 列表中的值
        """
        return self.client.lrange(key, start, end)

    # ---- 集合（Set）操作 ----
    def sadd(self, key: str, *values: str) -> int:
        """
        向集合中添加元素
        :param key: 集合名称
        :param values: 要添加的元素（可多个）
        :return: 添加成功的元素数量
        """
        return self.client.sadd(key, *values)

    def smembers(self, key: str) -> Set[str]:
        """
        获取集合中的所有元素
        :param key: 集合名称
        :return: 元素集合
        """
        return self.client.smembers(key)

    def srem(self, key: str, *values: str) -> int:
        """
        从集合中移除元素
        :param key: 集合名称
        :param values: 要移除的元素（可多个）
        :return: 成功删除的元素数量
        """
        return self.client.srem(key, *values)

    # ---- 其他操作 ----
    def keys(self, pattern: str = '*') -> List[str]:
        """
        获取所有匹配的键
        :param pattern: 键的匹配模式，默认匹配所有键（'*'）
        :return: 符合条件的键列表
        """
        return self.client.keys(pattern)

    def flush_db(self) -> None:
        """
        清空当前数据库（注意：会删除所有数据！）
        """
        self.client.flushdb()


if __name__ == '__main__':
    startup_nodes = [
        {"host": "atomue.nyau2z.clustercfg.apne1.cache.amazonaws.com", "port": 6379}
    ]

    redis_client = RedisClient(startup_nodes=startup_nodes)

    key = 'spot.convert.currency.avg.price.1c36549a64834a29a67bae538f395d6d.20250305'
    value = '90002'
    redis_client.set(key, value)
    print(redis_client.get(key))
