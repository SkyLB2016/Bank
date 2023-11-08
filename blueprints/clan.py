import requests

host = "https://api.253.com/"
appId = "jZj9NbUM"
appKey = "Z0crr4Ct"


# {'chargeStatus': 1, 'message': '成功', 'data': {'orderNo': '011698896659123283', 'handleTime': '2023-11-02 11:44:19', 'result': '01', 'remark': '认证一致', 'bankName': '中国工商银行', 'cardType': 'E时代卡', 'cardCategory': '借记卡'}, 'code': '200000'}
def card_two_auth(name, cardNo):
    url = host + "open/bankcard/card-two-auth"
    data = {"appId": appId, "appKey": appKey, "name": name, "cardNo": cardNo}
    # response = requests.post(url, data=data, headers={'Content-Type': data.content_type})
    response = requests.post(url, data=data)
    return response.json()
    # if response.status_code == 200:
    #     return response.json()
    # else:
    #     return response.status_code
    # else:return ""


def card_three_auth(name, idNum, cardNo):
    url = host + "open/bankcard/card-three-auth"
    data = {"appId": appId, "appKey": appKey, "name": name, "idNum": idNum, "cardNo": cardNo}
    response = requests.post(url, data=data)
    return response.json()
    # if response.status_code == 200:
    #     return response.json()
    # else:
    #     return response.status_code
#
