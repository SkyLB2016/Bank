import random
import re

from flask import Blueprint, request, jsonify, session
import json

from sqlalchemy.exc import IntegrityError

from exts import db
from models import UserModel, TokenModel

bp = Blueprint("user", __name__, url_prefix="/user")

SUCCESS = 200
FAIL = 400


@bp.route('/login', methods=['post'])
def login():
    # phone = request.form['phone']
    # phone = request.form.get('phone')
    # password = request.form['password']
    phone = request.json['phone']
    password = request.json['password']

    if not validate_phone_number(phone):
        return jsonify({"status": FAIL, "message": "手机号格式不正确"})
    user = UserModel.query.filter_by(phone=phone).first()
    if not user:
        return jsonify({"status": FAIL, "message": "用户不存在"})
    # if check_password_hash(user.password, password):
    if not password == user.password:
        return jsonify({"status": FAIL, "message": "密码错误"})
    # session['user_id'] = user.id
    # 生成32位的随机数
    token = generate_random_string(32)
    token_model = TokenModel.query.filter_by(user_id=user.id).first()
    if token_model:
        token_model.token = token
    else:
        token_model = TokenModel(token=token, user_id=user.id)
        db.session.add(token_model)

    try:
        db.session.commit()
    except SyntaxError:
        return jsonify({"status": SUCCESS, "message": "登录失败", "token": None})
    # finally:
    #     "已注册"

    return jsonify({"status": SUCCESS, "message": "成功", "token": token, "userName": user.username})


def generate_random_string(length):
    characters = "0123456789"
    result = ""
    for i in range(length):
        result += random.choice(characters)
    print(result)
    return result


def validate_phone_number(phone_number):
    pattern = r"1[3456789]\d{9}"
    match = re.match(pattern, phone_number)
    if match:
        return True
    else:
        return False


@bp.route('/register')
def register():
    # phone = "13703288210"
    # password = "123456"
    username = "甲乙"
    phone = "18531022252"
    password = "123456"
    user = UserModel.query.filter_by(phone=phone).first()
    if user:
        return jsonify({"status": FAIL, "message": "已注册", "token": None})

    user = UserModel(username=username, phone=phone, password=password)
    # password = generate_password_hash("123456"))

    db.session.add(user)
    try:
        db.session.commit()
    except  IntegrityError:
        return jsonify({"status": FAIL, "message": "已注册", "token": None})
    except SyntaxError:
        return jsonify({"status": FAIL, "message": "已注册", "token": None})
    # else:
    #      "已注册"
    finally:
        "已注册"

    return "成功"
