from flask import Flask
from applications.middle_ware.before_request import before_request


def middle_ware_init(app: Flask) -> None:

    @app.before_request
    def __before_request():
        return before_request()
