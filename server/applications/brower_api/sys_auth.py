import base64
import os

from flask import Blueprint

from applications.common.resp import Resp
from setting import API_PREFIX
from setting import FILE_UPLOAD_PATH
from exts import db, redis
from applications.library.captcha import generate_captcha
from applications.library.jwt_library import create_jwt_token
from applications.library.parse_req_data import process_requset_data
from applications.library.password_md5 import password_md5
from applications.model.sys_user import User


bp = Blueprint(
    __file__.replace('.', ''),
    __file__,
    url_prefix=API_PREFIX + '/sys_auth'
)


# 获取验证码
@bp.route('/captcha', methods=['GET'])
def get_captcha():
    captcha_image, captcha_id = generate_captcha(130, 35)

    # 将图片数据转换为 base64 编码
    base64_image = base64.b64encode(captcha_image).decode('utf-8')
    # 构造一个可以直接嵌入到 HTML 中的图片数据
    base64_string = f"data:image/png;base64,{base64_image}"

    # 返回 JSON 响应包含 base64 字符串和 captcha_id
    return Resp.success({
        'captcha_image': base64_string,
        'captcha_id': captcha_id
    })


# 登录
@bp.route('/login', methods=['POST'])
def login():
    params = process_requset_data()
    username: str = params.get('username')
    password: str = params.get('password')
    captcha_id: str = params.get('captcha_id')
    captcha_text: str = params.get('captcha_text')

    if not username or not password or not captcha_text:
        return Resp.fail('用户名, 密码, 验证码 不能为空!')

    captcha_sour_text: bytes = redis.get(captcha_id)

    # fixme 测试 记得恢复
    # if not captcha_sour_text or captcha_sour_text.decode().upper() != captcha_text.upper():
    #     return Result.fail('验证码错误！')

    # 根据用户名查询用户
    user: User = User.query.filter(
        User.username == username,
        User.password == password_md5(password),
    ).first()

    if not user:
        return Resp.fail('用户名或密码错误！')

    if not user.is_active:
        return Resp.fail('用户已被禁用，如需启用请联系管理员！')

    token = create_jwt_token(user.id, user.username)

    return Resp.success({'token': token}, '登录成功！')


# 注册
@bp.route('/register', methods=['POST'])
def register():
    params = process_requset_data()

    username: str = params.get('username')
    password: str = params.get('password')
    captcha_id: str = params.get('captcha_id')
    captcha_text: str = params.get('captcha_text')

    if not username or not password or not captcha_text:
        return Resp.fail('缺少必填项')

    # fixme 测试 记得恢复
    # captcha_sour_text: bytes = redis.get(captcha_id)
    #
    # if not captcha_sour_text or captcha_sour_text.decode().upper() != captcha_text.upper():
    #     return Resp.fail('验证码错误！')

    if User.query.filter(User.username == username).first():
        return Resp.fail('用户名重复！')

    try:
        new_user = User(
            username=username,
            password=password_md5(password)
        )
        db.session.add(new_user)
        db.session.commit()

        # 创建用户的资源文件夹, 以用户id做为目录名
        user_file_path = FILE_UPLOAD_PATH / 'user' / str(new_user.id)  # todo路径问题
        if not os.path.exists(user_file_path):
            os.makedirs(user_file_path)

        return Resp.success(None, '注册成功！')
    except Exception:
        db.session.rollback()
        return Resp.fail(f'注册失败')
