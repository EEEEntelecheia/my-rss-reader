# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import atexit

from app.utils.feed_fetcher import fetch_all_feeds

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

    # 启动定时任务（只在主进程中启动一次）
    if not app.debug or os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        # 避免 Flask 调试模式下的双重启动
        scheduler = BackgroundScheduler()
        scheduler.add_job(
            func=lambda: app.app_context().push() or fetch_all_feeds(),
            trigger=IntervalTrigger(hours=1),
            id='fetch_all_feeds',
            name='每小时抓取所有订阅源',
            replace_existing=True
        )
        scheduler.start()
        # 确保程序退出时关闭调度器
        atexit.register(lambda: scheduler.shutdown())

    # 注册蓝图（稍后我们创建蓝图）
    from .routes import main_bp
    app.register_blueprint(main_bp)

    # 创建数据库表（可选，根据需求）
    with app.app_context():
        db.create_all()      # 首次运行时会根据模型创建表

    return app