from flask import request


def process_requset_data() -> dict:
    print(request.path, request.json)
    return request.json


