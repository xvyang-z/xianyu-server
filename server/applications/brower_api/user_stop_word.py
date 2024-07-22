from flask import Blueprint

from applications.model.user_stop_word import StopWord
from setting import API_PREFIX
from exts import db
from applications.library.parse_req_data import process_requset_data
from applications.common.resp import Resp

from flask.globals import g

bp = Blueprint(
    __file__.replace('.', ''),
    __file__,
    url_prefix=API_PREFIX + '/user_stop_word',
)


# 新增
@bp.route('/create', methods=['POST'])
def create_stop_word():
    params = process_requset_data()
    word = params['word']

    old_word = StopWord.query.filter(
        StopWord.word == word
    ).first()

    if old_word:
        return Resp.fail('违禁词已存在，不能重复添加！')

    try:
        stop_word = StopWord(
            word=word,
            user_id=g.user_info.id,
        )
        db.session.add(stop_word)
        db.session.commit()
        return Resp.success(None, '新增成功！')
    except Exception:
        db.session.rollback()
        return Resp.fail(f'新增失败！')


# 编辑
@bp.route('/update', methods=['POST'])
def update_stop_word():
    params = process_requset_data()
    id_ = params['id']
    word = params['word']

    stop_word = StopWord.query.filter(
        StopWord.id == id_,
        StopWord.user_id == g.user_info.id
    ).first()
    if not stop_word:
        return Resp.fail('该id对应的违禁词不存在！')

    same_word: StopWord = StopWord.query.filter(
        StopWord.user_id == g.user_info.id,
        StopWord.word == word
    ).first()
    if stop_word.word != word and same_word:
        return Resp.fail('违禁词已存在，不可重复！')

    stop_word.word = word

    try:
        db.session.commit()
        return Resp.success(None, '编辑成功！')
    except Exception:
        db.session.rollback()
        return Resp.fail('编辑失败！')


# 删除
@bp.route('/delete', methods=['POST'])
def delete_stop_word():
    params = process_requset_data()
    ids = params['ids']

    StopWord.query.filter(
        StopWord.id.in_(ids),
        StopWord.user_id == g.user_info.id
    ).delete()

    try:
        db.session.commit()
        return Resp.success(None, '删除成功！')
    except Exception:
        db.session.rollback()
        return Resp.fail('删除失败！')


# 分页
@bp.route('/paging', methods=['POST'])
def paging():
    params = process_requset_data()
    page = params.get('page', 1)
    per_page = params.get('per_page', 10)
    word = params['query_args'].get('word')

    query = StopWord.query

    if word:
        query = query.filter(StopWord.word.contains(word))

    paginate = query.paginate(page=page, per_page=per_page, error_out=False)

    items = []
    for item in paginate.items:
        item: StopWord
        items.append({
            'id': item.id,
            'word': item.word,
        })

    resp = {
        'page': paginate.page,
        'per_page': paginate.per_page,
        'total': paginate.total,
        'items': items
    }

    return Resp.success(resp)


# 详情
@bp.route('/detail/<int:id_>', methods=['GET'])
def detail(id_):
    stop_word: StopWord = StopWord.query.get(id_)
    return Resp.success({
        'id': stop_word.id,
        'word': stop_word.word
    })
