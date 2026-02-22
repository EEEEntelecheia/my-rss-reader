# app/routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from .models import Feed, Article  # 从 models 导入
from app.utils.feed_fetcher import fetch_feed

main_bp = Blueprint('main', __name__)

# 首页
@main_bp.route('/')
def index():
    articles = Article.query.order_by(Article.published.desc()).all()
    return render_template('index.html', articles=articles)
# 显示所有订阅源
@main_bp.route('/feeds')
def feeds():
    feeds = Feed.query.all()
    return render_template('feeds.html', feeds=feeds)

# 添加订阅源
@main_bp.route('/feed/add', methods=['GET', 'POST'])
def add_feed():
    if request.method == 'POST':
        name = request.form.get('name')
        url = request.form.get('url')

        # 简单校验
        if not name or not url:
            flash('名称和URL都不能为空')
            return redirect(url_for('main.add_feed'))

        # 检查是否已存在
        if Feed.query.filter_by(url=url).first():
            flash('该RSS源已存在')
            return redirect(url_for('main.add_feed'))

        # 创建 Feed 记录
        feed = Feed(name=name, url=url)
        db.session.add(feed)
        db.session.commit()

        # 首次添加时抓取一次文章（可选）
        try:
            fetch_feed(url)
            flash('订阅源添加成功，并已抓取文章')
        except Exception as e:
            flash(f'订阅源添加成功，但首次抓取失败: {str(e)}')

        return redirect(url_for('main.index'))

    return render_template('add_feed.html')


# 删除订阅源
@main_bp.route('/feed/delete/<int:feed_id>')
def delete_feed(feed_id):
    feed = Feed.query.get_or_404(feed_id)
    # 删除关联文章（可选，数据库设置了级联删除的话可省略）
    Article.query.filter_by(feed_id=feed.id).delete()
    db.session.delete(feed)
    db.session.commit()
    flash('订阅源已删除')
    return redirect(url_for('main.index'))


# 查看某个订阅源的文章（可选）
@main_bp.route('/feed/<int:feed_id>')
def feed_articles(feed_id):
    feed = Feed.query.get_or_404(feed_id)
    articles = feed.articles.order_by(Article.published.desc()).all()
    return render_template('articles.html', articles=articles, feed=feed)

@main_bp.route('/articles')
def articles():
    # 文章列表
    articles = Article.query.order_by(Article.published.desc()).all()
    return render_template('articles.html', articles=articles)
