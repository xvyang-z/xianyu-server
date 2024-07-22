from flask import Blueprint

from setting import API_PREFIX

bp = Blueprint(
    __file__.replace('.', ''),
    __name__,
    url_prefix=API_PREFIX + '/user_product'
)

from applications.brower_api.user_product.location import location
from applications.brower_api.user_product.user_product import *
