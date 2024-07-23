import json

from flask import Blueprint
from flask.globals import g

from applications import enum
from applications.common.resp import Resp
from applications.model.user_device import Device
from applications.model.user_product_to_device import ProductToDevice
from applications.model.user_task import Task
from setting import API_PREFIX
from exts import db
from applications.library.parse_req_data import process_requset_data

bp = Blueprint(
    __file__.replace('.', ''),
    __file__,
    url_prefix=API_PREFIX + '/user_device_to_product',
)


# 分页
@bp.route('/paging', methods=['POST'])
def paging():
    params = process_requset_data()
    page = params.get('page', 1)
    per_page = params.get('per_page', 10)
    device_id = params['query_args'].get('device_id')
    publish_state = params['query_args'].get('publish_state')
    desc = params['query_args'].get('desc')

    query = (
        ProductToDevice.query
        .join(Device, ProductToDevice.device_id == Device.id)
        .filter(ProductToDevice.user_id == g.user_info.id)
        .add_columns(Device.device_name)
        .order_by(ProductToDevice.id.desc())
    )

    if device_id:
        query = query.filter(ProductToDevice.device_id == device_id)
    if publish_state:
        query = query.filter(ProductToDevice.publish_state == publish_state)
    if desc:
        query = query.filter(ProductToDevice.desc == desc)

    paginate = query.paginate(page=page, per_page=per_page, error_out=False)

    items = []
    for item in paginate.items:
        p2d: ProductToDevice = item[0]
        items.append({
            'id': p2d.id,
            'device_name': item.device_name,
            'price': p2d.price,
            'desc': p2d.desc,
            'images': p2d.images,
            'publish_state': p2d.publish_state,
            'is_in_operation': p2d.is_in_operation,
            'publish_time': p2d.publish_time,
            'location': p2d.location,
        })

    resp = {
        'page': paginate.page,
        'per_page': paginate.per_page,
        'total': paginate.total,
        'items': items,
    }

    return Resp.success(resp)


# 删除设备商品
@bp.route('/delete', methods=['POST'])
def delete():
    params = process_requset_data()

    ids = params['ids']

    results: list[ProductToDevice] = (
        ProductToDevice.query
        .filter(
            ProductToDevice.id.in_(ids),
            ProductToDevice.user_id == g.user_info.id,
            ProductToDevice.is_in_operation == False,
        )
    ).all()

    if len(results) != len(ids):
        return Resp.fail("正在操作中, 不可以删除, 请刷新界面重试")

    tasks = []
    for item in results:
        item.is_in_operation = True

        task = Task(
            user_id=g.user_info.id,
            device_id=item.device_id,
            cmd=enum.Task.cmd.删除商品,
            cmd_args={
                'id': item.id,
                'price': item.price,
                'desc': item.desc,
                'is_delist': item.publish_state == enum.ProductToDevice.publish_state.已下架
            }
        )
        tasks.append(task)

    db.session.add_all(tasks)

    try:
        db.session.commit()
        return Resp.success(None, '已加入任务列表, 手机端删除成功后会自动删除')
    except Exception:
        db.session.rollback()
        return Resp.fail('加入任务列表失败')


# 下架设备商品
@bp.route('/delist', methods=['POST'])
def delist():
    params = process_requset_data()

    ids = params['ids']

    results: list[ProductToDevice] = (
        ProductToDevice.query
        .filter(
            ProductToDevice.id.in_(ids),
            ProductToDevice.user_id == g.user_info.id,
            ProductToDevice.publish_state == enum.ProductToDevice.publish_state.已发布,
            ProductToDevice.is_in_operation == False,
        )
    ).all()

    if len(results) != len(ids):
        return Resp.fail("选中的商品 不是已发布的商品 或 正在操作中, 请刷新界面重试")

    tasks = []
    for item in results:
        item.is_in_operation = True

        task = Task(
            user_id=g.user_info.id,
            device_id=item.device_id,
            cmd=enum.Task.cmd.下架商品,
            cmd_args={
                'id': item.id,
                'price': item.price,
                'desc': item.desc,  # 通过价格和描述去定位要下架的商品
            }
        )
        tasks.append(task)

    db.session.add_all(tasks)

    try:
        db.session.commit()
        return Resp.success(None, '已加入任务列表, 手机端下架成功后会自动修改为下架状态')
    except Exception:
        db.session.rollback()
        return Resp.fail('加入任务列表失败')


# 重新发布下架的商品
@bp.route('/republish', methods=['POST'])
def republish():
    params = process_requset_data()

    ids = params['ids']

    results: list[ProductToDevice] = (
        ProductToDevice.query
        .filter(
            ProductToDevice.id.in_(ids),
            ProductToDevice.user_id == g.user_info.id,
            ProductToDevice.publish_state == enum.ProductToDevice.publish_state.已下架,
            ProductToDevice.is_in_operation == False,
        )
    ).all()

    if len(results) != len(ids):
        return Resp.fail("选中的商品 不是已下架的商品 或 正在操作中, 请刷新界面重试")

    tasks = []
    for item in results:
        item.is_in_operation = True

        task = Task(
            user_id=g.user_info.id,
            device_id=item.device_id,
            cmd=enum.Task.cmd.重新上架,
            cmd_args={
                'id': item.id,
                'price': item.price,
                'desc': item.desc,
            }
        )
        tasks.append(task)

    db.session.add_all(tasks)

    try:
        db.session.commit()
        return Resp.success(None, '已加入任务列表, 重新上架成功后会自动修改为下架状态')
    except Exception:
        db.session.rollback()
        return Resp.fail('加入任务列表失败')


# 降价
@bp.route('/reduce_price', methods=['POST'])
def reduce_price():
    params = process_requset_data()

    ids = params['ids']

    results: list[ProductToDevice] = (
        ProductToDevice.query
        .filter(
            ProductToDevice.id.in_(ids),
            ProductToDevice.user_id == g.user_info.id,
            ProductToDevice.publish_state == enum.ProductToDevice.publish_state.已发布,
            ProductToDevice.is_in_operation == False,
            ProductToDevice.price > 16
        )
    ).all()

    if len(results) != len(ids):
        return Resp.fail("选中的商品 不是已发布的商品 或 正在操作中 或 此时金额小于等于16, 请刷新界面重试")

    tasks = []
    for item in results:
        item.is_in_operation = True

        task = Task(
            user_id=g.user_info.id,
            device_id=item.device_id,
            cmd=enum.Task.cmd.商品降价,
            cmd_args={
                'id': item.id,
                'price': item.price,
                'desc': item.desc,
            }
        )
        tasks.append(task)

    db.session.add_all(tasks)

    try:
        db.session.commit()
        return Resp.success(None, '已加入任务列表, 降价成功后会自动修改价格')
    except Exception:
        db.session.rollback()
        return Resp.fail('加入任务列表失败')
