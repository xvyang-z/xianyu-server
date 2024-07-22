import uuid
from flask import Blueprint, request, g

from applications.common.resp import Resp
from applications.library.file_path import UploadPath
from applications.model.user_product import Product

bp = Blueprint(
    __file__.replace('.', ''),
    __file__,
    url_prefix='/upload'
)


# todo 图片类型校验


# 用户自己上传用户头像
@bp.route('/user_avatar', methods=['POST'])
def user_avatar():

    user_id = g.user_info.id
    files = request.files.getlist('file')  # 获取文件列表
    filenames = []

    # 遍历文件列表
    for file in files:

        file_prefix = uuid.uuid4().hex
        file_suffix = file.filename.split('.')[-1]

        new_filename = f'{file_prefix}.{file_suffix}'

        user_avatar_dir = UploadPath.get_user_avatar_dir(user_id=user_id)
        file.save(user_avatar_dir.abs_path / new_filename)
        filenames.append({
            'src_name': file.filename,
            "file_path": f'{user_avatar_dir.router_path}/{new_filename}',
        })

    # 返回成功响应，包括所有上传的文件名
    return Resp.success(filenames, '上传成功！')


# 管理员在 系统设置 - 用户管理 界面上传用户头像
@bp.route('/sys_user_avatar', methods=['POST'])
def sys_user_avatar():
    user_id = int(request.form['id'])
    files = request.files.getlist('file')  # 获取文件列表
    filenames = []

    # 遍历文件列表
    for file in files:

        file_prefix = uuid.uuid4().hex
        file_suffix = file.filename.split('.')[-1]

        new_filename = f'{file_prefix}.{file_suffix}'

        user_avatar_dir = UploadPath.get_user_avatar_dir(user_id=user_id)
        file.save(user_avatar_dir.abs_path / new_filename)
        filenames.append({
            'src_name': file.filename,
            "file_path": f'{user_avatar_dir.router_path}/{new_filename}',
        })

    # 返回成功响应，包括所有上传的文件名
    return Resp.success(filenames, '上传成功！')


# 上传商品图片 (这个接口 客户端 和 浏览器端 都用到了)
# 新增商品前上传图片, 仅携带 product_uuid, 这个 product_uuid 由前端或客户端生成, 可以分次上传, 保证同一个商品上传图片时这个值相同即可
# 修改商品的图片, 仅携带商品的 id
@bp.route('/user_product_img', methods=['POST'])
def user_product_img():
    id_: str = request.form.get('id', None)
    product_uuid: str = request.form.get('product_uuid', None)

    if id_ is not None and product_uuid is not None:
        return Resp.fail('id 或 uuid 不能同时存在')

    if id_ is not None:  # 修改商品图片
        product: Product = Product.query.get(int(id_))
        if product is None:
            return Resp.fail('商品不存在')

        uuid_ = product.uuid

    else:  # 新增商品前上传图片
        uuid_ = product_uuid

    user_id = g.user_info.id
    files = request.files.getlist('files')  # 获取文件列表
    filenames = []

    # 遍历文件列表
    for file in files:
        file_prefix = uuid.uuid4().hex
        file_suffix = file.filename.split('.')[-1]

        new_filename = f'{file_prefix}.{file_suffix}'

        user_product_dir = UploadPath.get_user_product_dir(user_id=user_id, product_uuid=uuid_)
        file.save(user_product_dir.abs_path / new_filename)
        filenames.append({
            'src_name': file.filename,
            'file_path': f'{user_product_dir.router_path}/{new_filename}',
        })

    # 返回成功响应，包括所有上传的文件名
    return Resp.success(filenames, '上传成功！')


# 站点图片上传
@bp.route('/sys_logo', methods=['POST'])
def sys_logo():

    files = request.files.getlist('files')  # 获取文件列表
    filenames = []

    # 遍历文件列表
    for file in files:
        file_prefix = uuid.uuid4().hex
        file_suffix = file.filename.split('.')[-1]

        new_filename = f'{file_prefix}.{file_suffix}'

        sys_dir = UploadPath.get_sys_dir()
        file.save(sys_dir.abs_path / new_filename)
        filenames.append({
            'src_name': file.filename,
            "file_path": f'{sys_dir.router_path}/{new_filename}',
        })

    # 返回成功响应，包括所有上传的文件名
    return Resp.success(filenames, '上传成功！')
