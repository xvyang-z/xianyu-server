import re

from flask import Blueprint, g

from applications import enum
from applications.common.resp import Resp
from applications.library.parse_req_data import process_requset_data
from applications.model.user_device import Device
from applications.model.user_task import Task
from exts import db
from setting import API_PREFIX, ADB_TCP_PORT_SUFFIX

bp = Blueprint(
    __file__.replace('.', ''),
    __file__,
    url_prefix=API_PREFIX + '/user_device',
)


# 分页
@bp.route('/paging', methods=['POST'])
def paging():
    params = process_requset_data()

    page = params.get('page', 1)
    per_page = params.get('per_page', 10)

    device_flag = params['query_args'].get("device_flag")

    query = (
        Device.query
        .filter(
            Device.user_id == g.user_info.id,
        )
        .order_by(Device.id.desc())
    )

    if device_flag:
        query = query.filter(Device.device_flag.contains(device_flag))

    paginate = query.paginate(page=page, per_page=per_page, error_out=False)

    items = []
    for item in paginate.items:
        item: Device
        items.append({
            'id': item.id,
            'device_flag': item.get_device_flag_without_suffix(),
            'device_name': item.device_name,
            'is_open_fish_shop': item.is_open_fish_shop,
        })

    resp = {
        'page': paginate.page,
        'per_page': paginate.per_page,
        'total': paginate.total,
        'items': items
    }
    return Resp.success(resp)


@bp.route('/create', methods=['POST'])
def create():
    params = process_requset_data()
    device_flag: str = params["device_flag"]
    device_name: str = params["device_name"]
    is_open_fish_shop: bool = params["is_open_fish_shop"]

    # 仅检查设备标识的格式
    if '.' in device_flag:
        if not re.match(r'^(\d{1,3}\.){3}\d{1,3}$', device_flag):
            return Resp.fail('检测到 设备标识 是 无线连接, 但格式有误, 应是 一个正确的ip地址')

        # 真正的无线设备标识 带后缀的
        device_flag_true = device_flag + ADB_TCP_PORT_SUFFIX

    else:
        if not re.match(r'^[A-Za-z0-9]*$', device_flag):
            return Resp.fail('检测到 设备标识 是 有线连接, 但格式有误, 应是一串 仅包含大小写字母和数字的字符')

        device_flag_true = device_flag

    # 检查是否有重复的标识
    if Device.query.filter(
            Device.device_flag == device_flag_true,
            Device.user_id == g.user_info.id,
    ).first():
        return Resp.fail('该 设备标识 已存在')

    # 如果设备名存在, 则检查是否有重复的设备名
    if device_name:
        if Device.query.filter(
                Device.device_name == device_name,
                Device.user_id == g.user_info.id,
        ).first():
            return Resp.fail('已存在 相同的 设备名')

    # 如果设备名不存在, 则给一个默认的设备名, 和 设备标识 保持一致
    else:
        device_name = device_flag

    device = Device(
        is_open_fish_shop=is_open_fish_shop,
        device_flag=device_flag_true,
        device_name=device_name,
        user_id=g.user_info.id,
    )

    db.session.add(device)
    try:
        db.session.commit()
        return Resp.success(None, '绑定成功')
    except Exception:
        db.session.rollback()
        return Resp.fail('绑定失败')


# 解绑
@bp.route('/delete', methods=['POST'])
def delete_xianyu_account():
    params = process_requset_data()
    ids = params['ids']

    running_task_on_devide = Task.query.filter(
        Task.device_id.in_(ids),
        Task.cmd_state.in_([
            enum.Task.cmd_state.运行中,
            enum.Task.cmd_state.重试中,
        ])
    ).all()

    if running_task_on_devide:
        return Resp.fail('设备有正在运行的任务不能删除！')

    Device.query.filter(Device.id.in_(ids)).delete()

    try:
        db.session.commit()
        return Resp.success(None, '删除成功！')

    except Exception:
        db.session.rollback()
        return Resp.fail('删除失败！')


# 编辑
@bp.route('/update', methods=['POST'])
def update():
    params = process_requset_data()

    device_id: int = params["id"]
    device_name: str = params["device_name"]
    device_flag: str = params["device_flag"]
    is_open_fish_shop: bool = params["is_open_fish_shop"]

    if not device_name:
        return Resp.fail('设备名不能为空')

    if '.' in device_flag:
        if not re.match(r'^(\d{1,3}\.){3}\d{1,3}$', device_flag):
            return Resp.fail('检测到 设备标识 是 无线连接, 但格式有误, 应是 一个正确的ip地址')

        # 真正的无线设备标识 带后缀的
        device_flag_true = device_flag + ADB_TCP_PORT_SUFFIX

    else:
        if not re.match(r'^[A-Za-z0-9]*$', device_flag):
            return Resp.fail('检测到 设备标识 是 有线连接, 但格式有误, 应是一串 仅包含大小写字母和数字的字符')

        device_flag_true = device_flag

    try:
        device: Device = Device.query.get(device_id)
        if not device:
            return Resp.fail('设备不存在！')

        # 检查是否有重复的标识
        if (
                device_flag != device.get_device_flag_without_suffix() and
                Device.query.filter(
                    Device.device_flag == device_flag_true,
                    Device.user_id == g.user_info.id,
                ).first() is not None
        ):
            return Resp.fail('设备标识重复')

        if (
                device_name != device.device_name and
                Device.query.filter(
                    Device.device_name == device_name,
                    Device.user_id == g.user_info.id,
                ).first() is not None
        ):
            return Resp.fail('设备名重复')

        device.device_name = device_name
        device.device_flag = device_flag_true
        device.is_open_fish_shop = is_open_fish_shop

        db.session.commit()
        return Resp.success(None, '编辑成功！')
    except Exception:
        db.session.rollback()
        return Resp.fail('编辑失败！')


# 详情
@bp.route('/detail/<int:id_>', methods=['GET'])
def detail(id_):
    device: Device = Device.query.get(id_)
    if device is None:
        return Resp.fail("没有这个设备id")

    resp = {
        'id': device.id,
        'device_flag': device.get_device_flag_without_suffix(),
        'device_name': device.device_name,
        'is_open_fish_shop': device.is_open_fish_shop,
    }
    return Resp.success(resp)


# 设备列表
@bp.route('/list', methods=['GET'])
def list_():
    devices: list[Device] = Device.query.filter(Device.user_id == g.user_info.id).order_by(Device.id.desc()).all()

    lst = []
    for device in devices:
        lst.append({
            'id': device.id,
            'device_name': device.device_name,
        })

    return Resp.success(lst)
