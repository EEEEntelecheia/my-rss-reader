# app/routes.py
from flask import Blueprint, render_template
from .models import Feed, Article  # 从 models 导入

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    # 你的首页逻辑
    feeds = Feed.query.all()
    return render_template('index.html', feeds=feeds)

@main_bp.route('/articles')
def articles():
    # 文章列表
    articles = Article.query.order_by(Article.published.desc()).all()
    return render_template('articles.html', articles=articles)