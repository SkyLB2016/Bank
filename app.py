from flask import Flask, render_template
from flask_migrate import Migrate

import config
from blueprints.user import bp as user_bp
from blueprints.bank import bp as bank_bp
from exts import db

app = Flask(__name__)
# 绑定配置文件
app.config.from_object(config)

db.init_app(app)  # 绑定数据库

migrate = Migrate(app, db)

app.register_blueprint(user_bp)
app.register_blueprint(bank_bp)


@app.route('/')
def index():  # put application's code here
    return render_template("index.html")
    # return render_template("test.html")
    # return "index.html"


if __name__ == '__main__':
    app.run()
