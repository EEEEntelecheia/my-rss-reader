# app/models.py
from . import db
from datetime import datetime

class Feed(db.Model):
    __tablename__ = 'feeds'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)        # 订阅源名称
    url = db.Column(db.String(200), unique=True, nullable=False)  # RSS地址
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    articles = db.relationship('Article', backref='feed', lazy='dynamic')

class Article(db.Model):
    __tablename__ = 'articles'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    link = db.Column(db.String(200), unique=True, nullable=False)
    published = db.Column(db.DateTime)
    summary = db.Column(db.Text)
    is_read = db.Column(db.Boolean, default=False)
    feed_id = db.Column(db.Integer, db.ForeignKey('feeds.id'))