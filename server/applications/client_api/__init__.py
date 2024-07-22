from flask import Blueprint, Flask
from setting import CLIENT_API_PREFIX


__bp = Blueprint(
    __file__.replace('.', ''),
    __file__,
    url_prefix=CLIENT_API_PREFIX
)


def client_api_init(app: Flask):
    from applications.client_api.get_task import get_task
    from applications.client_api.exec_fail import exec_fail
    from applications.client_api.check_token_expire import check_token_expire

    from applications.client_api.success.crawl import crawl
    from applications.client_api.success.delete import delete
    from applications.client_api.success.delist import delist
    from applications.client_api.success.publish import publish
    from applications.client_api.success.republish import republish
    from applications.client_api.success.reduce_price import reduce_price

    app.register_blueprint(__bp)
