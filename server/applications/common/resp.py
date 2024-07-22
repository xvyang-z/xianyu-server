from flask import jsonify


# 封装返回json响应结果类
class Resp:
    @staticmethod
    def success(data=None, message="操作成功"):
        return jsonify({
            "code": 0,
            "success": True,
            "data": data,
            "message": message
        })

    @staticmethod
    def fail(message="操作失败"):
        return jsonify({
            "code": 1,
            "success": False,
            "data": None,
            "message": message
        })
