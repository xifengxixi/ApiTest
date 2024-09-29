# 1. 前言

本项目为接口自动化测试框架，python+requests+pytest+allure+yaml+log+oracle+钉钉通知

- 项目参与者：溪风习习
- 个人语雀地址：[https://www.yuque.com/xifengxixi](https://gitee.com/link?target=https%3A%2F%2Fwww.yuque.com%2Fxifengxixi)
- 技术支持邮箱：1107872406@qq.com

需要练习的朋友可以查看本人语雀项目，有相关笔记。需要教程的朋友，可加Q私信

如果对您有帮助，请点亮本项目的小星星，不胜感激。

# 2. 一级关键字

必须有的四个一级关键字：name、base_url、request、validate

# 3. 二级关键字

在request一级关键字下必须包含有两个二级关键字：method、url

# 4. 传参方式

在request一级关键字下，通过二级关键字参数传参。

- 如果是get请求，通过params传参。
- 如果是post请求：

    - 传json格式，通过json关键字传参。
    - 传表单格式，通过data关键字传参。(如请求类型为query)
    - 传文件格式，通过files关键字传参，如:

```
files:  
    media: "E:/shu.png"  
    media: "E\\shu.png" # \\防止转义
```

​        参数中若请求头为application/json，但参数结构为键值对的字典，则必须用json传参。

# 5. 接口关联

## 5.1. 提取：必须使用一级关键字：extract

- json提取方式

```
extract:  
    token: token
```

- jsonpath提取方式

```
extract:  
    applyName: $.data.rows[0].applyName  
```

- 正则表达式提取方式

```
extract:  
    token: '"token":"(.*?)"' # yaml中格式需要，不能这样写："token":"(.*?)"，否则会报错
```

- 图片验证码提取方式

```
extract:  
    image_code: ${get_image_code}
```

- 支持同时提取多个元素，分为两种情况：

​        yaml文件中

```
extract:  
    token: token  
    setPwd: setPwd
```

​       参数化，csv文件中

```
extract:  
    tb_token:token-setPwd:setPwd     # (纯json提取方式)  
    tb_token:'"token":"(.*?)"'-setPwd:setPwd     # (包含正则表达式提取方式)
```

- 支持提取指定第几次出现的元素，通过jsonpath提取!!!
- 支持按顺序提取同一元素(如一个查询接口返回3个满足条件的id，可按如下方式依次提取该3个id，支持json提取和正则表达式提取混用)：

```
extract:  
    id_total: id  
    id_goods: '"id":"(.*?)"'  
    id_car: '"id":"(.*?)"' 
```

## 5.2. 取值：支持以下两种取值方式，注意格式!!!

- ${}

```
${get_extract(token)}
```

- {{}}

```
"{{token}}"
```

# 6. 热加载

当yaml需要使用动态参数时，那么可以在debug_talk.py文件中写方法调用(注意强转类型)

注意：传参时，需要什么类型的数据，需要做强转。int(min)， int(max)

```python
# 获取随机数
def get_random_number(self， min， max):
    return random.randint(int(min)， int(max))
```

# 7. 断言

支持的断言方式有：equals、contains

- 状态断言：

```
- equals: {status_code: 200}
```

- 业务断言：

```
- equals: {code: 0} 
- contains: token
```

支持同时断言多个条件，分为两种情况：

- yaml文件中

```
validate:  
    -   equals: {status_code: 200}  
    -   equals: {code: 0}  
    -   contains: token
```

- 参数化，csv文件中

```
validate:  
    equals:{status_code:200}-equals:{code:0}-contains:token
```

# 8. 数据驱动

使用csv和一级关键字parameters实现，如：

- yaml写法：

```yaml
parameters:
  name-account-code-pwd-extract-validate: data/test_02_login.csv
name: $csv{name}
account: $csv{account}
```

- csv写法：

```plain
name,account,code,pwd,extract,validate
提报人登录,vJzarh1FCgzAvcJJybJRzA==,"${get_extract_file(image_code)}",1a8f04ad2d17eee8a6bbe029ae597461,tb_token:'"token":"(.*?)"',equals:{status_code:200}-equals:{code:0}-contains:token
审核人登录,hPgw6BimkHqH4fvc92xSsA==,"${get_extract_file(image_code)}",1a8f04ad2d17eee8a6bbe029ae597461,sh_token:token,equals:{status_code:200}-equals:{code:0}
调度登录,cu6OeWcLNpnRG+9rnd0YAw==,"${get_extract_file(image_code)}",1a8f04ad2d17eee8a6bbe029ae597461,dd_token:token,equals:{status_code:200}-equals:{code:0}
承运商登录,8xN7ce2ayKl1dPzFEdXQsA==,"${get_extract_file(image_code)}",1a8f04ad2d17eee8a6bbe029ae597461,cys_token:token,equals:{status_code:200}-equals:{code:0}
```

注意：不使用csv进行数据驱动时，请勿填写yaml文件中parameters，否则将会执行parameters。(可以不写关键字parameters，也可以parameters为空)

csv中请求体中若某字段需要传列表或字典，可按如下格式：

```plain
['1'-'2']  ==>  ['1'，'2']
{"1":"2"-"3":"4"}  ==>  {"1":"2"，"3":"4"}
```

# 9. 日志监控、异常处理以及基础路径的设置

日志调用：
```plain
logger.debug("这是一个debug信息")

logger.info("这是一个info信息")

logger.warning("这是一个warning信息")

logger.error("这是一个error信息")

logger.critical("这是一个critical信息")
```
​    

# 10. 数据库校验及提取

- yaml写法：

```yaml
db:
  jsonpath: 
      -   $.data.orderType
  type: 
      -   ==
  value: 
      -   '[0]["ORDER_TYPE"]'
  dbextract:
      orderId_car: '[0]["ID"]'
  sql:
      -   select * from ORDER_INFO where ORDER_NO = '$json{$.data.orderNo}'
```

1. jsonpath(列表格式)

指接口返回结果的jsonpath，可通过该项在返回结果中取值

2. type(列表格式)

指数据库查询后判断接口返回结果中的值与数据库查询的值的关系(当前仅支持==、in)

3. value(列表格式)

指数据库查询后获取数据库查询的值(sql查询后返回数据为字典列表格式，注意取值格式！！！)

4. dbextract(字典格式)

指数据库查询后是否提取查询结果中的某一项的值

5. sql(列表格式)

指数据库查询的sql语句，支持多条sql语句查询

若sql语句中有需要替换的部分：$json{此处为需要替换的值}

- csv写法：

```plain
name,jsonpath,type,value,dbextract,sql
提报值班计划参数化测试,$.data.orderType-$.data.id,in-==,[0]["ORDER_TYPE"]-[0]["ID"],orderType_car:[0]["ORDER_TYPE"]-orderId_car:[1]["ID"],select * from ORDER_INFO where ORDER_NO = '$json{$.data.orderNo}'-select ID from ORDER_INFO where ORDER_NO = '$json{$.data.orderNo}'
```

注意：csv中value和dbextract中取数据库查询后的值的格式需与例子严格一致，当前框架dbextract仅支持一种提取方式!!!

# 11. 自动生成py文件

先编写用例yaml，然后运行automatic_util.py工具自动生成py文件!!!
