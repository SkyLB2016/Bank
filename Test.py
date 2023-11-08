# import requests
# import pandas as pd
#
#
# # GET 请求
# def data_get(pageNum, pageSize, appsecret, url):
#     '''
#     pageNum: 页数
#     pageSize: 每页个数(不超过200)
#     appsecret: 应用识别码(申请获得)
#     url: api 接口
#     '''
#     # 以字典形式编辑查询参数
#     parameters = {'pageNum': pageNum, 'pageSize': pageSize, 'appsecret': appsecret}
#
#     # 发送 GET 请求，返回一个包含服务器响应信息的 response 对象
#     response = requests.get(url=url, params=parameters)
#
#     # HTTP 响应状态码为 200 表示请求成功，服务器成功处理了请求
#     if response.status_code == 200:
#         # 响应信息中status为 1，表示成功获取数据
#         if response.json()['status'] == 1:
#             ## 提取响应结果中返回的数据data，并转换为dataframe
#             data = pd.DataFrame(response.json()['data'])
#         else:
#             # 响应信息中status不为 1，表示获取数据失败，需进一步检查原因
#             print(response.json())
#     else:
#         # HTTP 响应状态码不为 200 时，提示“URL未正常响应请求”
#         raise Exception('URL未正常响应请求')
#     return data
#
#
# data = data_get(pageNum=1,
#                 pageSize=200,
#                 appsecret='申请的 APP 识别码',
#                 url='http://data.zjzwfw.gov.cn/jdop_front/interfaces/cata_18444/get_data.do')
# data
#
#
# # POST 请求
# def data_post(pageNum, pageSize, appsecret, url):
#     # 以字典形式编辑请求体
#     data_value = {'pageNum': pageNum, 'pageSize': pageSize, 'appsecret': appsecret}
#     # 发送 POST 请求，返回一个包含服务器响应信息的 response 对象
#     response = requests.post(url=url, data=data_value)
#
#     if response.status_code == 200:
#         # 响应信息中status为1，表示成功获取数据
#         if response.json()['status'] == 1:
#             data = pd.DataFrame(response.json()['data'])
#         else:
#             print(response.json())
#     else:
#         raise Exception('URL未正常响应请求')
#     return data
#
#
# data = data_post(pageNum=1,
#                  pageSize=200,
#                  appsecret='申请的 APP 识别码',
#                  url='http://data.zjzwfw.gov.cn/jdop_front/interfaces/cata_18444/get_data.do')
