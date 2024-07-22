import json
import os
import shutil
import uuid
from typing import Any

from flask.globals import g

from applications import enum
from applications.brower_api.user_product import bp
from applications.common.resp import Resp
from applications.library.file_path import UploadPath
from applications.model.prod_location import Location
from applications.model.user_product import Product
from applications.model.user_product_to_device import ProductToDevice
from applications.model.user_task import Task
from exts import db
from applications.library.parse_req_data import process_requset_data


# 爬取咸鱼商品
@bp.route('/crawl', methods=['POST'])
def crawl():

    params = process_requset_data()
    keyword = params['keyword']
    device_id = params['device_id']

    # 加入任务
    task = Task(
        user_id=g.user_info.id,
        device_id=device_id,
        cmd=enum.Task.cmd.爬取商品,
        cmd_args={
            "keyword": keyword,
        }
    )
    db.session.add(task)

    try:
        db.session.commit()
        return Resp.success(None, '已加入任务列表, 请到任务列表中查看')
    except Exception:
        db.session.rollback()
        return Resp.fail('加入任务列表失败!')


# 手动新增商品
@bp.route('/create', methods=['POST'])
def create():
    params = process_requset_data()

    uuid_: str = params['uuid']
    desc: str = params['desc']
    price: float = params['price']
    images: list = params['images']

    if len(images) == 0:
        return Resp.fail('至少上传一张图片')

    user_id = g.user_info.id

    product = Product(
        user_id=user_id,
        desc=desc,
        price=price,
        images=images,
        uuid=uuid_
    )

    db.session.add(product)

    try:
        db.session.commit()
        return Resp.success(None, '新增成功')
    except Exception as e:
        db.session.rollback()
        return Resp.fail('新增失败')


# 发布商品
@bp.route('/publish', methods=['POST'])
def publish():
    params = process_requset_data()
    device_ids: list[int] = params['device_ids']
    product_ids: list[int] = params['product_ids']
    location_ids: list[int] = params['location_ids']

    if len(device_ids) == 0 or len(product_ids) == 0:
        return Resp.fail('发布失败，请至少选择一个 要发布的产品 和 要执行发布操作的的设备！')

    if len(device_ids) != len(set(device_ids)) or len(product_ids) != len(set(product_ids)):
        return Resp.fail('发布失败，设备 或 商品 的 id 重复！')

    # 要发布的设备 和 发布商品 的 id 联合枚举
    will_publish = []
    for device_id in device_ids:
        for product_id in product_ids:
            will_publish.append(
                (device_id, product_id)
            )

    # 确认 product_ids 和 查询到的结果条数对应
    products: list[Product] = Product.query.filter(
        Product.id.in_(product_ids),
        Product.user_id == g.user_info.id
    ).all()
    if len(products) != len(product_ids):
        return Resp.fail('数据有变动, 请刷新界面后再试')

    pid_product: dict[int, Product] = {}
    for product in products:
        pid_product[product.id] = product

    if location_ids:
        province_id, city_id, county_id = location_ids

        locations: list[Location] = Location.query.filter(Location.id.in_(location_ids)).all()
        id_to_name = {}
        for location in locations:
            id_to_name[location.id] = location.name

        province, city, county = id_to_name[province_id], id_to_name[city_id], id_to_name[county_id]

        loc = [province, city, county]
    else:
        loc = []

    # 下面有复制文件的操作, 这个变量用于出错时删除复制的文件
    __will_del_path_when_error = []

    # 加入任务, 商品数据以添加任务的那一刻为准
    p2ds: list[ProductToDevice] = []
    for device_id, product_id in will_publish:
        product = pid_product[product_id]

        # 将要发布的产品复制一份到新目录, 如果不复制, 当删除商品模板时在发布页面会找不到图片
        new_uuid = uuid.uuid4().hex
        product_dir = UploadPath.get_user_product_dir(g.user_info.id, product.uuid)
        publish_dir = UploadPath.get_user_publish_dir(g.user_info.id, new_uuid)

        new_imgs = []
        for img_file in os.listdir(product_dir.abs_path):
            shutil.copy2(product_dir.abs_path / img_file, publish_dir.abs_path / img_file)
            new_imgs.append(publish_dir.router_path + f'/{img_file}')

        __will_del_path_when_error.append(publish_dir.abs_path)

        p2d = ProductToDevice(
            uuid=new_uuid,
            price=product.price,
            desc=product.desc,  # todo 去除违禁词
            images=new_imgs,
            location=loc,
            publish_state=enum.ProductToDevice.publish_state.发布中,
            is_in_operation=True,
            user_id=g.user_info.id,
            device_id=device_id,
        )
        p2ds.append(p2d)

    db.session.add_all(p2ds)

    db.session.flush()  # 刷新后会提交到暂存区, 自增 id 被填充值

    tasks = []
    for p2d in p2ds:
        task = Task(
            user_id=g.user_info.id,
            device_id=p2d.device_id,
            cmd=enum.Task.cmd.发布商品,
            cmd_args={
                'id': p2d.id,
                'uuid': p2d.uuid,
                'price': p2d.price,
                'desc': p2d.desc,
                'images': p2d.images,
                'location': p2d.location,
            }
        )
        tasks.append(task)

    db.session.add_all(tasks)
    try:
        db.session.commit()
        return Resp.success(None, '已加入任务列表, 请到任务列表中查看')
    except Exception:
        for i in __will_del_path_when_error:
            shutil.rmtree(i)
        db.session.rollback()
        return Resp.fail('发布失败')


# 编辑
@bp.route('/edit', methods=['POST'])
def edit():
    params = process_requset_data()

    product_id: int = params["product_id"]
    # uuid_: str = params['uuid']

    new_desc: str = params["desc"]
    new_imgs: list[str] = params["images"]
    new_price: float = params["price"]

    if len(new_imgs) == 0:
        return Resp.fail('商品至少有一张图片')

    product = Product.query.filter(
        Product.id == product_id,
        Product.user_id == g.user_info.id
    ).first()
    if not product:
        return Resp.fail('没有此商品，编辑失败！')

    # 这里检查一下文件名是否是 这个商品的, 防止删除其他的
    product_dir = UploadPath.get_user_product_dir(g.user_info.id, product.uuid)
    for img in new_imgs:
        if not img.startswith(product_dir.router_path):
            return Resp.fail('图片路径非法')

    old_imgs: list[str] = product.images

    if new_price == product.price and new_desc == product.desc and set(new_imgs) == set(old_imgs):
        return Resp.success('更新完成')

    # 对所有新图片的路由处理, 只剩最后的文件名
    new_imgs_name = []
    for new_img in new_imgs:
        new_imgs_name.append(new_img.replace(product_dir.router_path + '/', ''))

    # 遍历这个商品的图片目录, 删除 所有 不是新图片 的文件
    for img_file_name in os.listdir(product_dir.abs_path):
        if img_file_name not in new_imgs_name:
            os.remove(product_dir.abs_path / img_file_name)

    # 将编辑后的商品信息存入数据库
    product.images = new_imgs
    product.desc = new_desc
    product.price = new_price

    try:
        db.session.commit()
        return Resp.success(None, '编辑成功')
    except Exception:
        db.session.rollback()
        return Resp.fail('商品编辑失败!')


# 复制商品
@bp.route('/copy', methods=['POST'])
def copy():
    params = process_requset_data()
    src_product_id: int = params["src_product_id"]
    src_product: Product = Product.query.filter(
        Product.id == src_product_id,
        Product.user_id == g.user_info.id
    ).first()

    if src_product is None:
        return Resp.fail('商品不存在')

    src_uuid = src_product.uuid
    dst_uuid = uuid.uuid4().hex
    src_dir = UploadPath.get_user_product_dir(g.user_info.id, src_uuid).abs_path
    dst_dir = UploadPath.get_user_product_dir(g.user_info.id, dst_uuid).abs_path

    new_product = Product(
        uuid=dst_uuid,
        desc=src_product.desc,
        images=src_product.images.replace(src_product.uuid, dst_uuid),  # 图片路径中的旧目录也要替换成新的目录
        price=src_product.price
    )
    new_product.user_id = g.user_info.id
    db.session.add(new_product)

    # 将这个产品的图片也复制一份到新的目录中
    for item in os.listdir(src_dir):
        shutil.copy2(src_dir / item, dst_dir / item)

    try:
        db.session.commit()
        return Resp.success(None, '复制成功！')
    except Exception:
        db.session.rollback()
        return Resp.fail('复制失败！')


# 删除商品
@bp.route('/delete', methods=['POST'])
def delete():
    params = process_requset_data()

    ids = params['ids']

    # 查询出将要删除的商品
    will_be_del_products: list[Product] = (
        Product.query
        .filter(
            Product.id.in_(ids),
            Product.user_id == g.user_info.id,
        )
        .all()
    )

    # 删除商品 和 图片目录
    uuids = []
    for product in will_be_del_products:
        uuids.append(product.uuid)
        db.session.delete(product)

    try:
        db.session.commit()  # 数据库中数据成功删除后再删图片

        for uuid_ in uuids:
            product_img_dir = UploadPath.get_user_product_dir(g.user_info.id, uuid_).abs_path
            shutil.rmtree(product_img_dir)

        return Resp.success(None, '商品删除成功！')
    except Exception:
        db.session.rollback()
        return Resp.fail('发生错误，删除失败！')


# 详情
@bp.route('/detail/<int:id_>', methods=['GET'])
def detail(id_):
    product: Product = Product.query.filter(
        Product.id == id_,
        Product.user_id == g.user_info.id
    ).first()

    if product is None:
        return Resp.fail('商品不存在')

    return Resp.success({
        "desc": product.desc,
        "id": product.id,
        "images": product.images,
        "price": product.price,
        "user_id": product.user_id,
        "uuid": product.uuid
    })


# 分页
@bp.route('/paging', methods=['POST'])
def paging():
    params = process_requset_data()
    page: int = params.get('page', 1)
    per_page: int = params.get('per_page', 10)
    desc: dict[str, Any] = params['query_args']['desc']

    query = (
        Product.query.order_by()
        .filter(Product.user_id == g.user_info.id)
        .order_by(Product.id.desc())
    )

    if desc:
        query = query.filter(Product.desc.contains(desc))

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    # 添加是否发布的属性
    items = []
    for item in pagination.items:
        item: Product
        items.append({
            'id': item.id,
            'uuid': item.uuid,
            'desc': item.desc,
            'price': item.price,
            'images': item.images,
        })

    resp = {
        'page': pagination.page,
        'per_page': pagination.per_page,
        'total': pagination.total,
        'items': items
    }

    return Resp.success(resp)
