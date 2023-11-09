from flask import Blueprint
import json

from models import CLanAllModel, CLanModel

# json.dumps()	将 Python 对象编码成 JSON 字符串
# json.loads()	将已编码的 JSON 字符串解码为 Python 对象
# json.dump()	将Python内置类型序列化为json对象后写入文件
# json.load()	读取文件中json形式的字符串元素转化为Python类型

json_clan_test = {
    'chargeStatus': 1,
    'message': '成功',
    'data': {
        'orderNo': '011698896659123283',
        'handleTime': '2023-11-02 11:44:19',
        'result': '01',
        'remark': '认证一致',
        'bankName': '中国工商银行',
        'cardType': 'E时代卡',
        'cardCategory': '借记卡'
    },
    'code': '200000'
}


def json_test():
    # json.dumps(): 把字典(变量)转换成json字符串;
    text = json.dumps(json_clan_test)
    print(text)
    # json.loads(): 把json字符串转换成字典(变量);
    obj = json.loads(text)
    print(obj['chargeStatus'])
    print(obj)
    data = json_to_class(json_clan_test)
    print(data.code)
    print(data.data.orderNo)
    print(json.dumps(data))
    # data = json.loads(text, object_hook=json_to_class)
    # print(data.code)
    # print(data.data.orderNo)

    # json.dump():把字典(文件对象)转换成json字符串
    # text = json.dump(obj)
    # print(text)
    # json.load(): 把json字符串转换成字典(文件对象);
    # obj = json.load(text)
    # print(obj)
    return ""
    # return json_clan_test


def json_to_clan(temp):
    return CLanModel(
        temp['orderNo'],
        temp['handleTime'],
        temp['remark'],
        temp['result'],
        temp['bankName'],
        temp['cardType'],
        temp['cardCategory']
    )


def json_to_class(temp):
    return CLanAllModel(
        temp['chargeStatus'],
        temp['code'],
        temp['message'],
        json_to_clan(temp['data'])
    )
