from applications.brower_api.user_product import bp
from applications.common.resp import Resp
from applications.library.parse_req_data import process_requset_data
from applications.model.prod_location import Location


# 发布时获取位置
@bp.route('/location', methods=['POST'])
def location():
    params = process_requset_data()

    parent_id = params['id']

    # 请求第一级时 parent_id: 0
    if parent_id is None:
        parent_id = 0

    locs: list[Location] = Location.query.filter(Location.parent_id == parent_id).all()

    resp = []
    for loc in locs:
        resp.append(
            {
                'id': loc.id,
                'name': loc.name,
            }
        )

    return Resp.success(resp)
