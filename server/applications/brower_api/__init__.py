from flask import Flask


def brower_api_init(app: Flask):
    """
    初始化浏览器界面用到的路由
    """
    from applications.brower_api import sys_auth
    from applications.brower_api import user_product
    from applications.brower_api import sys_user
    from applications.brower_api import sys_sub
    from applications.brower_api import user_stop_word
    from applications.brower_api import sys_setting
    from applications.brower_api import user_device
    from applications.brower_api import user_product_to_device
    from applications.brower_api import user_task
    from applications.brower_api import user_user
    from applications.brower_api import upload
    from applications.brower_api import other_task

    app.register_blueprint(sys_auth.bp)
    app.register_blueprint(user_product.bp)
    app.register_blueprint(sys_user.bp)
    app.register_blueprint(sys_sub.bp)
    app.register_blueprint(user_stop_word.bp)
    app.register_blueprint(sys_setting.bp)
    app.register_blueprint(user_device.bp)
    app.register_blueprint(user_product_to_device.bp)
    app.register_blueprint(user_task.bp)
    app.register_blueprint(user_user.bp)
    app.register_blueprint(upload.bp)
    app.register_blueprint(other_task.bp)
