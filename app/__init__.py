# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from apscheduler.schedulers.background import BackgroundScheduler

# 初始化扩展（先不绑定 app）
db = SQLAlchemy()
scheduler = BackgroundScheduler()


def create_app(config_object=None):
    app = Flask(__name__)

    # 加载配置
    if config_object is None:
        # 默认使用开发配置
        app.config.from_object('config.DevConfig')
    else:
        app.config.from_object(config_object)

    # 初始化扩展（绑定 app）
    db.init_app(app)

    # 启动定时任务（如果还没启动）
    if not scheduler.running:
        scheduler.start()

    # 注册蓝图（稍后我们创建蓝图）
    from .routes import main_bp
    app.register_blueprint(main_bp)

    # 创建数据库表（可选，根据需求）
    with app.app_context():
        db.create_all()

    return app