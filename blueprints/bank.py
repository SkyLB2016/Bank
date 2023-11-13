import os
import os
import re
import time
from datetime import datetime

import xlrd
import xlsxwriter
from flask import Blueprint, jsonify, request, send_file, send_from_directory

from blueprints.ali import ali_bankcard_query
from blueprints.clan import card_two_auth, card_three_auth
from exts import db
from models import BankModel, RecordModel, UserModel, TokenModel

bp = Blueprint("bank", __name__, url_prefix="/bank")
SUCCESS = 200
FAIL = 400
INIT_ERROR = '06'
date = datetime.date(datetime.now())
# os.mkdir(path_root)  只能生成一级文件目录，多级生成会报错
# 上传文件保存的路径
path_root = f"file/upload/{date}/"
# 生成的错误文件保存的路径
path_root_error = f"file/error/{date}/"
# 生成的成功文件保存的路径
path_root_result = f"file/result/{date}/"


# json_clan_test = {
#     'chargeStatus': 1,
#     'message': '成功',
#     'data': {
#         'orderNo': '011698896659123283',
#         'handleTime': '2023-11-02 11:44:19',
#         'result': '01',
#         'remark': '认证一致',
#         'bankName': '中国工商银行',
#         'cardType': 'E时代卡',
#         'cardCategory': '借记卡'
#     },
#     'code': '200000'
# }
#

#
# json_ali = {
#     'error_code': 0,
#     'reason': '成功',
#     'result': {
#         'card': '6222020302059210872',
#         'province': '天津',
#         'city': '天津市',
#         'bank': '工商银行',
#         'type': '借记卡',
#         'cardname': 'E时代卡',
#         'tel': '95588',
#         'logo': 'gonghanglogo.gif',
#         'bankcode': '01020000'
#     }
# }

@bp.route('/test')
def test():
    print("请求数据前")
    # json_clan = card_two_auth("李彬", "6222020302059210872")
    print("请求数据后")
    return "成功"


@bp.route("/down", methods=['POST'])
def down_success():
    # type=request.args.get("type",1)
    path = request.args.get("path")
    return send_file(path, as_attachment=True)  # 返回保存的文件


@bp.route('/template', methods=['POST'])
def down_file():
    # 验证token
    # token = request.cookies.get('Authorization')
    # print(f"token=={token}")
    token = request.headers.get('Authorization')
    print(f"token=={token}")

    type_mode = request.args.get("type", default=1, type=int)
    filepath = 'file/down/type1.xlsx'
    if type_mode == 2:
        filepath = 'file/down/type2.xlsx'
    elif type_mode == 3:
        filepath = 'file/down/type3.xlsx'
    elif type_mode == 4:
        filepath = 'file/down/type4.xlsx'
    elif type_mode == 5:
        filepath = 'file/down/type5.xlsx'
    return send_file(filepath, as_attachment=True)  # 返回保存的文件


@bp.route("/record/list")
def record_list():
    # 验证token
    # headers 里的token
    token = request.headers.get('Authorization')
    print(f"token=={token}")
    # cookies 里的 token
    # token = request.cookies.get('Authorization')
    # print(f"token=={token}")
    if is_empty(token):
        return jsonify({"status": FAIL, "message": "尚未登录"})
    # 同一个变量名字，这里就是指向对象了
    token = TokenModel.query.filter_by(token=token).first()
    if not token:
        return jsonify({"status": FAIL, "message": "尚未登录"})
    # 根据token 获取用户id，验证用户
    user_id = token.user_id
    user = UserModel.query.get(user_id)
    if not user:
        return jsonify({"status": FAIL, "message": "用户不存在"})

    page = request.args.get("page", default=1, type=int)
    page_size = request.args.get("pageSize", default=10, type=int)

    # 开始查询数据
    record_sql = RecordModel.query.filter_by(user_id=user_id)
    # record_sql = RecordModel.query.filter_by(user_id=user_id).order_by(RecordModel.join_time)#默认排序，从小到大
    # record_sql = RecordModel.query.filter_by(user_id=user_id).order_by(RecordModel.join_time.desc())#降序排序，从大到小
    # 数据总共有多少条
    total = record_sql.count()
    print(f"总共有=={total}")
    # 数据当前的偏移量
    offset = (page - 1) * page_size
    # 根据偏移量获取数据
    records = record_sql.offset(offset).limit(page_size)
    data_result = []
    for record in records:
        temp = record.json()
        temp["userName"] = user.username
        data_result.append(temp)
    print(str(data_result))

    return jsonify({"status": SUCCESS, "message": "成功", "data": data_result, "total": total})


@bp.route("/card/query", methods=['POST'])
def card_query():
    type_mode = request.args.get("type", default=1, type=int)
    token = request.headers.get('Authorization')
    print(f"token=={token}")
    if is_empty(token):
        return jsonify({"status": FAIL, "message": "尚未登录"})
    token = TokenModel.query.filter_by(token=token).first()
    if not token:
        return jsonify({"status": FAIL, "message": "用户不存在"})

    user_id = token.user_id
    user = UserModel.query.get(user_id)
    if not user:
        return jsonify({"status": FAIL, "message": "用户不存在"})

    check_method = "姓名 + 银行卡号 + 银行类型"
    if type_mode == 2:
        check_method = "姓名 + 身份证号 + 银行卡号 + 银行类型"
    elif type_mode == 3:
        check_method = "获取银行卡号归属地 + 银行类型"
    elif type_mode == 4:
        check_method = "姓名 + 银行卡号 + 获取归属地 + 银行类型"
    elif type_mode == 5:
        check_method = "姓名 + 身份证号 + 银行卡号 + 获取归属地 + 银行类型"
    # print(f"{int(time.time() * 1000)}")
    # print(f"path_success=={path_success}")

    # 先插入记录，状态为： 校验中
    record = RecordModel(  # join_time=int(time.time() * 1000),
        # join_time=datetime.now,
        check_method=check_method,
        status="校验中",
        user_id=user_id)
    db.session.add(record)
    try:
        db.session.commit()
    except SyntaxError:
        print("添加记录失败")
    finally:
        "失败"
    # 开始校验数据，
    file = request.files['file']
    suffix = file.filename.split('.')[1]  # 获取文件的后缀，防止有修改
    if not (suffix == 'xlsx' or suffix == "xls"):
        return jsonify({"status": FAIL, "message": "文件格式不正确", "data": None})

    # print(f"type_mode=={type_mode}")
    # 1.解析文件,获取银行卡数据
    bank_list = get_bank_data(file, type_mode)

    bank_result = []
    # 2.开始请求对应的银行卡数据
    for bank in bank_list:
        bank_result.append(bank_card_query(bank, type_mode))

    # 3.区分错误信息和正确信息
    bank_success = []
    bank_error = []
    for bank in bank_result:
        if bank.bank_result_no == INIT_ERROR:
            bank_error.append(bank)
        else:
            bank_success.append(bank)

    # 4.1构建错误信息 xlsx
    path_error = ""
    if len(bank_error) > 0:
        if type_mode == 1 or type_mode == 4:
            xlsx_error = create_file_error_02(bank_error)
        elif type_mode == 2 or type_mode == 5:
            xlsx_error = create_file_error_03(bank_error)
        else:
            xlsx_error = create_file_error_01(bank_error)

        # 开始构建 错误信息xlsx
        # 检查文件夹是否存在
        if not os.path.exists(path_root_error): os.mkdir(path_root_error)
        path = f"{path_root_error}error_{int(time.time() * 1000)}.xlsx"
        path_error = create_file(xlsx_error, path)

    # 4.2构建成功信息 xlsx
    length_success = len(bank_success)
    if length_success == 0:
        db.session.delete(record)
        db.session.commit()
        return jsonify({
            "status": SUCCESS,
            "message": "成功",
            "successCount": length_success,
            "successPath": "",
            "errorCount": len(bank_error),
            "errorPath": path_error
        })

    xlsx_success = []
    # 获取 xlsx 文件所需要的数据
    if type_mode == 1:
        xlsx_success = create_file_01(bank_success)
    elif type_mode == 2:
        xlsx_success = create_file_02(bank_success)
    elif type_mode == 3:
        xlsx_success = create_file_03(bank_success)
    elif type_mode == 4:
        xlsx_success = create_file_04(bank_success)
    elif type_mode == 5:
        xlsx_success = create_file_05(bank_success)

    # 开始构建生成 xlsx 文件
    if not os.path.exists(path_root_result):
        os.mkdir(path_root_result)
    path = f"{path_root_result}result_{int(time.time() * 1000)}.xlsx"
    path_success = create_file(xlsx_success, path)

    record.path = path_success
    record.check_count = length_success
    record.status = "校验完成"
    try:
        db.session.commit()  # 更新数据
    except SyntaxError:
        print("更新记录失败")
    finally:
        "失败"

    return jsonify({"status": SUCCESS,
                    "message": "成功",
                    "successCount": length_success,
                    "successPath": path_success,
                    "errorCount": len(bank_error),
                    "errorPath": path_error
                    })
    # return send_file(path, as_attachment=True)  # 返回保存的文件
    # return jsonify({"status": 200, "message": '成功', "data": None})


def get_bank_data(file, type_mode):
    # names = file.filename.split('.')
    # name = names[0]  # 文件名称
    # suffix = names[1]  # 获取文件的后缀，防止有修改
    # print(f"后缀类型=={suffix}")
    # filename = f"bank_{name}_{int(time.time() / 1000)}"

    # 检查文件夹是否存在
    if not os.path.exists(path_root):
        os.mkdir(path_root)

    path = f'{path_root}{file.filename}'
    file.save(path)  # 将接收到的文件保存到本地
    # print(f"名字=={path}")

    # 解析 xlsx 数据
    table = xlrd.open_workbook(path)
    sheet = table.sheets()[0]
    # 要根据不同的 type_mode 区分如何 获取 xlsx 中的数据
    if type_mode == 1 or type_mode == 4:
        return get_sheet_data_two(sheet)
    elif type_mode == 2 or type_mode == 5:
        return get_sheet_data_three(sheet)
    else:
        return get_sheet_data_one(sheet)


def get_sheet_data_one(sheet):  # 一列有：银行卡
    bank_list = []
    for row in range(1, sheet.nrows):  # 获取每行数据
        bank_list.append(BankModel(bank_card=str(sheet.cell_value(row, 0))))
    return bank_list


def get_sheet_data_two(sheet):  # 两列有：姓名，银行卡
    bank_list = []
    for row in range(1, sheet.nrows):  # 获取每行数据
        bank_list.append(BankModel(
            name=str(sheet.cell_value(row, 0)),
            bank_card=str(sheet.cell_value(row, 1))
        ))
    return bank_list


def get_sheet_data_three(sheet):  # 三列有：姓名，身份证号，银行卡
    bank_list = []
    for row in range(1, sheet.nrows):  # 获取每行数据
        bank_list.append(BankModel(
            name=str(sheet.cell_value(row, 0)),
            person_card=str(sheet.cell_value(row, 1)),
            bank_card=str(sheet.cell_value(row, 2))
        ))
    return bank_list


def create_file_error_01(bank_error):
    data = [["银行卡号", "错误信息"]]
    for bank in bank_error:
        data.append([bank.bank_card, bank.bank_error])
    return data


def create_file_error_02(bank_error):
    data = [["姓名", "银行卡号", "错误信息"]]
    for bank in bank_error:
        data.append([bank.name, bank.bank_card, bank.bank_error])
    return data


def create_file_error_03(bank_error):
    data = [["姓名", "身份证号", "银行卡号", "错误信息"]]
    for bank in bank_error:
        data.append([bank.name, bank.person_card, bank.bank_card, bank.bank_error])
    return data


def create_file_01(bank_success):
    data = [["姓名", "银行卡号", "校验结果", "所属银行", "银行卡类型", "银行卡类别"]]
    for bank in bank_success:
        name = bank.name  # 姓名
        bank_card = bank.bank_card  # 银行卡号
        bank_result = bank.bank_result  # 校验结果（一致）
        bank_name = bank.bank_name  # 所属银行
        bank_type = bank.bank_type  # 银行卡类型（cardType,cardname）
        bank_category = bank.bank_category  # 银行卡类别(cardCategory,type)
        data.append([name, bank_card, bank_result, bank_name, bank_type, bank_category])
        join_time = bank.join_time
    return data


def create_file_02(bank_success):
    data = [["姓名", "身份证号", "银行卡号", "校验结果", "所属银行", "银行卡类型", "银行卡类别"]]
    for bank in bank_success:
        name = bank.name  # 姓名
        person_card = bank.person_card  # 身份证号
        bank_card = bank.bank_card  # 银行卡号
        bank_result = bank.bank_result  # 校验结果（一致）
        bank_name = bank.bank_name  # 所属银行
        bank_type = bank.bank_type  # 银行卡类型（cardType,cardname）
        bank_category = bank.bank_category  # 银行卡类别(cardCategory,type)
        join_time = bank.join_time
        data.append([name, person_card, bank_card, bank_result, bank_name, bank_type, bank_category])
    return data


def create_file_03(bank_success):
    data = [["银行卡号", "所属银行", "开户行所在省", "开户行所在市", "银行卡类型", "银行卡类别"]]
    for bank in bank_success:
        bank_card = bank.bank_card  # 银行卡号
        bank_name = bank.bank_name  # 所属银行
        bank_local_province = bank.bank_local_province  # 开户行所在省
        bank_local_city = bank.bank_local_city  # 开户行所在市
        bank_type = bank.bank_type  # 银行卡类型（cardType,cardname）
        bank_category = bank.bank_category  # 银行卡类别(cardCategory,type)
        join_time = bank.join_time
        data.append([bank_card, bank_name, bank_local_province, bank_local_city, bank_type, bank_category])
    return data


def create_file_04(bank_success):
    data = [["姓名", "银行卡号", "校验结果", "所属银行", "开户行所在省", "开户行所在市", "银行卡类型", "银行卡类别"]]
    for bank in bank_success:
        name = bank.name  # 姓名
        bank_card = bank.bank_card  # 银行卡号
        bank_result = bank.bank_result  # 校验结果（一致）
        bank_name = bank.bank_name  # 所属银行
        bank_local_province = bank.bank_local_province  # 开户行所在省
        bank_local_city = bank.bank_local_city  # 开户行所在市
        bank_type = bank.bank_type  # 银行卡类型（cardType,cardname）
        bank_category = bank.bank_category  # 银行卡类别(cardCategory,type)

        join_time = bank.join_time
        data.append(
            [name, bank_card, bank_result, bank_name, bank_local_province, bank_local_city, bank_type, bank_category])
    return data


def create_file_05(bank_success):
    data = [["姓名", "身份证号", "银行卡号", "校验结果", "所属银行", "开户行所在省", "开户行所在市", "银行卡类型",
             "银行卡类别"]]
    for bank in bank_success:
        name = bank.name  # 姓名
        person_card = bank.person_card  # 身份证号
        bank_card = bank.bank_card  # 银行卡号
        bank_result = bank.bank_result  # 校验结果（一致）
        bank_name = bank.bank_name  # 所属银行
        bank_local_province = bank.bank_local_province  # 开户行所在省
        bank_local_city = bank.bank_local_city  # 开户行所在市
        bank_type = bank.bank_type  # 银行卡类型（cardType,cardname）
        bank_category = bank.bank_category  # 银行卡类别(cardCategory,type)
        data.append(
            [name, person_card, bank_card, bank_result, bank_name, bank_local_province, bank_local_city, bank_type,
             bank_category])
    return data


def bank_card_query(bank, type_mode):
    json_clan = None
    json_ali = None
    # 五种类型都有银行卡，所以可以提取出来先一步校验
    # 不为空,验证长度，只验证国内银行卡
    if is_empty(bank.bank_card) or is_count(bank.bank_card):
        bank.bank_error = "银行卡位数不对"
        bank.bank_result_no = INIT_ERROR
        return bank
    # 正则验证
    if not validate_bank_card_number(bank.bank_card):
        bank.bank_error = "银行卡无效"
        bank.bank_result_no = INIT_ERROR
        return bank

    # 创蓝是1245
    if type_mode == 1 or type_mode == 4:  # 请求创蓝标准二要素
        if is_empty(bank.name):
            bank.bank_error = "名字不能为空"
            bank.bank_result_no = INIT_ERROR
            return bank
        # 姓名，银行卡号，校验结果，所属银行，银行卡类型，银行卡类别
        json_clan = card_two_auth(bank.name, bank.bank_card)
    elif type_mode == 2 or type_mode == 5:  # 请求创蓝标准三要素
        if is_empty(bank.name):
            bank.bank_error = "名字不能为空"
            bank.bank_result_no = INIT_ERROR
            return bank
        if is_empty(bank.person_card) or not validate_id_card(bank.person_card):
            bank.bank_error = "身份证号码无效"
            bank.bank_result_no = INIT_ERROR
            return bank
        # 姓名，身份证号，银行卡号，校验结果，所属银行，银行卡类型，银行卡类别
        json_clan = card_three_auth(bank.name, bank.person_card, bank.bank_card)

    # 阿狸云的type_mode 是 345
    if type_mode == 2 or type_mode == 3 or type_mode == 4:  # 请求阿狸云
        # 银行卡号，所属银行，开户行所在省，开户行所在市，银行卡类型，银行卡类别
        json_ali = ali_bankcard_query(bank.bank_card)

    # print(f"请求的数据clan=={json_clan}")
    # print(f"请求的数据ali=={json_ali}")

    if json_clan:
        if json_clan['code'] == '200000':
            handle_clan_data(json_clan, bank)
        else:  # 此条数据错误，只填写错误信息
            bank.bank_result_no = '04'
            bank.bank_result = json_clan['message']
            # bank.bank_error = json_clan['message']
    if json_ali:
        bank.bank_result_no = '05'
        if json_ali['error_code'] == 0:
            handle_ali_data(json_ali, bank)
        else:
            bank.bank_error = json_ali['reason']

    # print(f"合成的数据bank=={bank.json()}")
    return bank


def handle_clan_data(clan, bank):
    data = clan['data']
    # 姓名，身份证号，银行卡号，
    # 创蓝只需要： 校验结果，所属银行，银行卡类型，银行卡类别
    bank.bank_result = data['remark']  # 校验结果
    bank.bank_result_no = data['result']  # 校验编号
    # if not bank.bank_result_no == "01": return
    bank.bank_name = data['bankName']  # 所属银行
    bank.bank_type = data['cardType']  # 银行卡类型
    bank.bank_category = data['cardCategory']  # 银行卡类别
    bank.join_time = f"{int(datetime.now().timestamp() * 1000)}"


def handle_ali_data(ali, bank):
    data = ali['result']
    # 创蓝和阿里一起请求的时候，阿里正常只需要： 开户行所在省，开户行所在市，
    bank.bank_local_province = data['province']
    bank.bank_local_city = data['city']
    # 当所属银行，银行卡类型，银行卡类别为空时，添加
    if bank.bank_name:
        bank.bank_name = data['bank']  # 银行卡类型
    if bank.bank_type:
        bank.bank_type = data['cardname']  # 银行卡类型
    if bank.bank_category:
        bank.bank_category = data['type']  # 银行卡类别
    bank.join_time = f"{int(datetime.now().timestamp() * 1000)}"


def create_file(data_result, path):
    # data = [
    #     ["姓名", "银行卡号"],
    #     ["李彬", "6222020302059210872"],
    #     ["李彬", "6231680001001129204"],
    #     ["李彬", "6214680067783769"],
    #     ["李林", "6217850200007539878"]
    # ]
    # print(f"data_result=={data_result}")
    workbook = xlsxwriter.Workbook(path)
    worksheet = workbook.add_worksheet()
    # worksheet.set_column()
    title_format = workbook.add_format(
        {
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': True
        }
    )
    for row, row_data in enumerate(data_result):
        worksheet.write_row(row, 0, row_data, title_format)
    workbook.close()
    return path


def validate_bank_card_number(card_number):
    # 银行卡号的正则表达式
    pattern = r'^[1-9]\d{14,19}$'
    # 使用正则表达式进行匹配
    if re.match(pattern, card_number):
        return True
    else:
        return False


def validate_id_card(id_card):
    # 身份证号码的正则表达式
    pattern = r'^[1-9]\d{5}(19|20)\d{2}(0[1-9]|1[0-2])(0[1-9]|[1-2]\d|3[0-1])\d{3}(\d|X)$'
    # 使用正则表达式进行匹配
    if re.match(pattern, id_card):
        return True
    else:
        return False


def is_empty(text):
    return text is None or len(text) == 0


def is_count(text):
    length = len(text)
    return not (length == 16 or length == 17 or length == 19)


@bp.route("/card/first")
def card_first():
    return jsonify({"status": SUCCESS, "message": "成功", "data": None})
