from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_migrate import Migrate
from sqlalchemy import text

from applications.brower_api import brower_api_init
from applications.client_api import client_api_init
from applications.common.json_proviewer import UpdatedJSONProvider
from applications.middle_ware import middle_ware_init
from applications.model import load_model

from setting import FILE_UPLOAD_PATH, DB_CFG, RDB_CFG

from exts import db, redis


app = Flask(__name__)
app.debug = True

app.json.ensure_ascii = False
app.json = UpdatedJSONProvider(app)

# 这行代码提供了 flask-migrate 所需的app对象和db对象
# 当执行 flask db migrate 时, 会加载这两个对象 然后就可以访问到数据库
# 然后将: 数据库现有结构, 当前模型类, 历史迁移脚本, 比对后决定要不要生成新的迁移脚本
# 如果有新的迁移脚本生成, 执行 flask db upgrade 则会运行迁移脚本将数据库更新
migrate = Migrate(app, db)

CORS(app)

# 初始化数据库连接信息
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{DB_CFG.user}:{DB_CFG.passwd}@{DB_CFG.host}:{DB_CFG.port}/{DB_CFG.db}?client_encoding=utf8'
db.init_app(app)

# 将模型类导入， 否则无法感知到这些类的存在也就创建不了表
load_model()

# 创建所有表
with app.app_context():
    db.create_all()

# 初始化 redis 连接信息
app.config['REDIS_URL'] = f'redis://{RDB_CFG.host}:{RDB_CFG.port}/{RDB_CFG.db}'
redis.init_app(app)

# 注册 后台系统 路由
brower_api_init(app)

# 注册 client_api 的路由
client_api_init(app)

# 添加中间件
middle_ware_init(app)


# 图片文件的静态路由
@app.route('/uploads/<path:filename>')
def upload_file(filename):
    return send_from_directory(FILE_UPLOAD_PATH, filename)


# fixme 创建一些地区的测试数据
# with app.app_context():
#     try:
#         db.session.execute(
#             text('''INSERT INTO "prod_location" ("id", "level", "parent_id", "name") VALUES
#             (1, 1, 0, '北京'),
#             (2, 1, 0, '广东'),
#             (3, 2, 1, '北京'),
#             (4, 2, 2, '广州'),
#             (5, 3, 3, '东城区'),
#             (6, 3, 3, '西城区'),
#             (7, 3, 4, '番禺区'),
#             (8, 3, 4, '白云区');''')
#         )
#     except Exception as e:
#         ...
#     db.session.commit()
# ## fixme end
