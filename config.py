# MYSQL所在的主机名
HOSTNAME = "127.0.0.1"
# HOSTNAME = "localhost"
# MYSQL监听的端口号，默认3306
PORT = 3306
# 连接MySQL的用户名，自定义的
USERNAME = "root"
# 连接MySQL的密码，自定义的
PASSWORD = "1qaz2wsx"
# MySQL创建的数据库名称，自定义的
DATABASE = "python"
# DB_URI = f"mysql+pymysql://{USERNAME}:{PASSWORD}@{HOSTNAME}:{PORT}/{DATABASE}?charset=utf8mb4"
DB_URI = "mysql+pymysql://{}:{}@{}:{}/{}?charset=utf8".format(USERNAME, PASSWORD, HOSTNAME, PORT, DATABASE)

SQLALCHEMY_DATABASE_URI = DB_URI
