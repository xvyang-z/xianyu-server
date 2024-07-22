from flask import Blueprint

from applications.common.resp import Resp
from applications.model.sys_sub import Sub
from setting import API_PREFIX
from exts import db
from applications.library.parse_req_data import process_requset_data

bp = Blueprint(
    __file__.replace('.', ''),
    __file__,
    url_prefix=API_PREFIX + '/sys_sub',
)


# 分页
@bp.route('/paging', methods=['POST'])
def paging():
    params = process_requset_data()
    page = params.get('page', 1)
    per_page = params.get('per_page', 10)
    name = params['query_args'].get('name')

    query = Sub.query

    if name != '':
        query = query.filter(Sub.name.contains(name))

    paginate = query.paginate(page=page, per_page=per_page, error_out=False)

    items = []
    for item in paginate.items:
        item: Sub
        items.append({
            'id': item.id,
            'name': item.name,
            'price': item.price,
            'detail': item.detail,
            'duration': item.duration,
        })

    resp = {
        'page': paginate.page,
        'per_page': paginate.per_page,
        'total': paginate.total,
        'items': items,
    }

    return Resp.success(resp)


# 创建会员订阅
@bp.route('/create', methods=['POST'])
def create():
    params = process_requset_data()

    detail = params['detail']
    duration = params['duration']
    name = params['name']
    price = params['price']

    if Sub.query.filter_by(name=name).first():
        return Resp.fail('会员订阅名称不能重复！')

    try:
        new_sub = Sub(
            detail=detail,
            duration=duration,
            name=name,
            price=price
        )
        db.session.add(new_sub)
        db.session.commit()
        return Resp.success(None, '新增成功！')
    except Exception:
        db.session.rollback()
        return Resp.fail('添加失败')


# 删除
@bp.route('/delete', methods=['POST'])
def delete():
    params = process_requset_data()
    ids: list[int] = params['ids']

    try:
        Sub.query.filter(Sub.id.in_(ids)).delete()
        db.session.commit()
        return Resp.success(None, '删除成功！')
    except Exception:
        db.session.rollback()
        return Resp.fail('删除失败')


# 编辑会员订阅
@bp.route('/update', methods=['POST'])
def update():
    params = process_requset_data()

    id_ = params["id"]
    duration = params["duration"]
    detail = params["detail"]
    name = params["name"]
    price = params["price"]

    sub = Sub.query.get(id_)

    same_sub = Sub.query.filter(Sub.name == name).first()
    if sub.name != name and same_sub is not None:
        return Resp.fail('已存在相同的订阅名称')

    sub: Sub = Sub.query.get(id_)
    if not sub:
        return Resp.fail('没有此会员订阅')

    sub.duration = duration
    sub.detail = detail
    sub.name = name
    sub.price = price

    try:
        db.session.commit()
        return Resp.success(None, '编辑成功！')
    except Exception:
        db.session.rollback()
        return Resp.fail('编辑失败')


# 详情
@bp.route('/sub_info/<int:sub_id>', methods=['GET'])
def sub_info(sub_id):
    sub: Sub = Sub.query.get(sub_id)
    if not sub:
        return Resp.fail('未查询到该订阅')

    data = {
        'id': sub.id,
        'name': sub.name,
        'price': sub.price,
        'detail': sub.detail,
        'duration': sub.duration,
    }

    return Resp.success(data)


# 会员订阅列表
@bp.route('/list', methods=['GET'])
def list_():
    subscriptions = Sub.query.all()
    lst = [{'subscription_id': subscription.id, 'name': subscription.name} for subscription in subscriptions]
    return Resp.success(lst)
