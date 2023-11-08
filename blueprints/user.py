from flask import Blueprint
import json

bp = Blueprint("user", __name__, url_prefix="/user")
# json.dumps(): 把字典(变量)转换成json字符串;
# json.loads(): 把json字符串转换成字典(变量);
# json.dump():把字典(文件对象)转换成json字符串
# json.load(): 把json字符串转换成字典(文件对象);


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

@bp.route('/json')
def json_test():
    # json.loads()
    return json.dumps(json_clan_test)
    # return json_clan_test
