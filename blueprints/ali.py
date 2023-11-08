import requests
from flask import Blueprint, render_template

host = 'https://bkaear.market.alicloudapi.com'
appkey = '203878781'
appcode = 'e7d3938941934a578954e75a8629f447'
app_secret = 'qcBVwGRAYAP1Ww7u0dwL7saBzBN0y9Gk'


def ali_bankcard_query(card):
    headers = {"authorization": "APPCODE " + appcode}
    response = requests.get(host + "/bankcard/query?card=" + card, headers=headers)
    # code = response.status_code
    return response.json()
    # if code == 200:
    #     return response.json()
    # else:
    #     return ""
    # print(f"code=={code}")
    # print(f"headers=={response.headers}")
    # data1 = response.json()
    # print(f"data1=={data1}")
    # result = data1['result']
    # print(f"result=={result}")
    # reason = data1['reason']
    # print(f"reason=={reason}")
    # error_code = data1['error_code']
    # print(f"error_code=={error_code}")
    # return render_template("index.html")
