from datetime import datetime
from exts import db


class UserModel(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(11), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False, )
    join_time = db.Column(db.DateTime, default=datetime.now)


class TokenModel(db.Model):
    __tablename__ = "token"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    token = db.Column(db.String(200), nullable=False)
    join_time = db.Column(db.DateTime, default=datetime.now)
    # 外键
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    # user = db.relationship(UserModel, backref="records")


class RecordModel(db.Model):
    __tablename__ = "record"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    path = db.Column(db.String(200), nullable=False)
    join_time = db.Column(db.DateTime, default=datetime.now)
    check_method = db.Column(db.String(40), default=False)
    check_count = db.Column(db.Integer, default=False)

    # 外键
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    # user = db.relationship(UserModel, backref="records")

    def json(self):
        return {
            "path": self.path,
            "joinTime": int(self.join_time.timestamp() * 1000),
            "checkMethod": self.check_method,
            "checkCount": self.check_count
        }


class BankModel(db.Model):
    __tablename__ = "bank"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # 姓名，身份证号，银行卡号，校验结果（一致），所属银行，开户行所在省，开户行所在市，银行卡类型，银行卡类别，错误信息
    name = db.Column(db.String(100), nullable=True)  # 姓名
    person_card = db.Column(db.String(100), nullable=True)  # 身份证号
    bank_card = db.Column(db.String(100), nullable=True)  # 银行卡号
    # 01 - 认证一致(收费); 02 - 认证不一致(收费); 03 - 认证不确定（不收费） 04 - 认证失败(不收费)，05 --代表阿狸云；06 代表xlsx获取的初始信息有误。
    bank_result_no = db.Column(db.String(20), nullable=True)  # 校验结果编号

    bank_result = db.Column(db.String(100), nullable=True)  # 校验结果（一致）
    bank_name = db.Column(db.String(100), nullable=True)  # 所属银行
    bank_local_province = db.Column(db.String(100), nullable=True)  # 开户行所在省
    bank_local_city = db.Column(db.String(100), nullable=True)  # 开户行所在市
    bank_type = db.Column(db.String(100), nullable=True)  # 银行卡类型（cardType,cardname）
    bank_category = db.Column(db.String(100), nullable=True)  # 银行卡类别(cardCategory,type)

    join_time = db.Column(db.String(20), default=f"{int(datetime.now().timestamp() * 1000)}")
    bank_error = db.Column(db.String(200), nullable=True)  # 错误信息

    def json(self):
        return {
            "name": self.name,
            "personCard": self.person_card,
            "bankCard": self.bank_card,
            "bankResult": self.bank_result,
            "bankName": self.bank_name,
            "bankLocalProvince": self.bank_local_province,
            "bankLocalCity": self.bank_local_city,
            "bankType": self.bank_type,
            "bankCategory": self.bank_category,
            "joinTime": self.join_time,
            "bankError": self.bank_error,
        }


# {
#     'chargeStatus': 1,
#     'message': '成功',
#     'data': {
#         'orderNo': '011698909108283496',
#         'handleTime': '2023-11-02 15:11:48',
#         'result': '01',
#         'remark': '认证一致',
#         'bankName': '中国工商银行',
#         'cardType': 'E时代卡',
#         'cardCategory': '借记卡'
#     },
#     'code': '200000'
# }
class CLanAllModel(object):
    # chargeStatus	int	1:收费；0：不收费
    # code	String	响应 code 码。200000：成功，其他失败。
    # message	String	响应 code 码解释
    # data	Object
    def __init__(self, chargeStatus, code, message, data):
        self.chargeStatus = chargeStatus
        self.code = code
        self.message = message
        self.data = data

    def json_to_class(self, json):
        return CLanAllModel(
            json['chargeStatus'],
            json['code'],
            json['message'],
            json['data']
        )


class CLanModel(object):

    # orderNo	String	业务唯一流水号。例：628291418130630
    # handleTime	String	查询时间 例：2018-04-09 15:05:01
    # remark	String	备注，例：一致
    # result	String	返回结果： 01-认证一致(收费) 02-认证不一致(收费) 03-认证不确定（不收费） 04-认证失败(不收费)
    # bankName	String	银行卡所属银行。样例：招商银行
    # cardType	String	银行卡类型 样例：金穗借记卡
    # cardCategory	String	银行卡类别 样例：借记卡
    def __init__(self, orderNo, handleTime, remark, result, bankName, cardType, cardCategory):
        self.orderNo = orderNo
        self.handleTime = handleTime
        self.remark = remark
        self.result = result
        self.bankName = bankName
        self.cardType = cardType
        self.cardCategory = cardCategory


# {
#   "error_code": 0,
#   "reason": "成功",
#   "result": {
#     "card": "6217000010023492492",
#     "province": "北京市",
#     "city": "北京",
#     "bank": "建设银行",
#     "type": "借记卡",
#     "cardname": "龙卡通",
#     "tel": "95533",
#     "logo": "jiansheyinhang.gif",
#     "bankcode": "01050000"
#   }
# }
class ALiAllModel(object):
    def __init__(self, result, reason, error_code):
        self.result = result
        self.reason = reason
        self.error_code = error_code


class ALiModel(object):
    def __init__(self, card, province, city, bank, type, cardname, tel, logo, bankcode):
        self.card = card
        self.province = province
        self.city = city
        self.bank = bank
        self.type = type
        self.cardname = cardname
        self.tel = tel
        self.logo = logo
        self.bankcode = bankcode
