import datetime
import json

from flask import g

from applications import enum
from applications.client_api import __bp
from applications.common.resp import Resp
from applications.model.user_product import Product
from applications.model.user_task import Task
from exts import db
from applications.library.parse_req_data import process_requset_data


@__bp.route('/success/crawl', methods=['POST'])
def crawl():
    """
    将爬取到的数据入库
    爬虫脚本执行后, 携带爬取的数据请求这个接口, 以同步系统内的数据
    """

    params = process_requset_data()

    task_id = params['task_id']
    products = params['products']

    try:
        import random
        # 将商品数据批量存入数据库
        new_products = []
        for product in products:
            new_products.append(Product(
                uuid=product['uuid'],
                price=product['price'],
                desc=product['desc'],
                images=product['images'],
                user_id=g.user_info.id,
            ))

        db.session.add_all(new_products)

        # 标记任务完成
        task: Task = Task.query.get(task_id)
        task.cmd_state = enum.Task.cmd_state.执行成功
        task.set_cmd_info('执行成功')
        task.end_time = datetime.datetime.utcnow()

        db.session.commit()
        return Resp.success()
    except Exception as e:
        db.session.rollback()
        return Resp.fail(str(e))
