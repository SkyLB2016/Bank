import wtforms
from phone import Phone


class LoginForm(wtforms.Form):
    phon1 = wtforms.StringField(validators=[Phone(message="手机格式错误！")])
    # password = wtforms.StringField(validators=[Length(min=6, max=20, message="密码格式错误！")])

