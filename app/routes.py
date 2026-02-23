# app/routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from .models import Feed, Article  # 从 models 导入
from app.utils.feed_fetcher import fetch_feed

main_bp = Blueprint("main", __name__)


# 首页
@main_bp.route("/")
def index():
    # 文章列表
    # 获取当前页码，默认为 1
    page = request.args.get("page", 1, type=int)
    # 每页显示 10 条
    per_page = 10

    # 使用 paginate 代替 all()
    pagination = Article.query.order_by(Article.published.desc()).paginate(
        page=page, per_page=per_page, error_out=False  # 如果 page 超出范围，返回空列表而不是 404
    )

    # pagination.items 是当前页的文章列表
    articles = pagination.items

    return render_template("index.html", articles=articles, pagination=pagination)


# 显示所有订阅源
@main_bp.route("/feeds")
def feeds():
    feeds = Feed.query.all()
    return render_template("feeds.html", feeds=feeds)


# 添加订阅源
@main_bp.route("/feed/add", methods=["GET", "POST"])
def add_feed():
    if request.method == "POST":
        name = request.form.get("name")
        url = request.form.get("url")

        # 简单校验
        if not name or not url:
            flash("名称和URL都不能为空")
            return redirect(url_for("main.add_feed"))

        # 检查是否已存在
        if Feed.query.filter_by(url=url).first():
            flash("该RSS源已存在")
            return redirect(url_for("main.add_feed"))

        # 创建 Feed 记录
        feed = Feed(name=name, url=url)
        db.session.add(feed)
        db.session.commit()

        # 首次添加时抓取一次文章（可选）
        try:
            fetch_feed(url)
            flash("订阅源添加成功，并已抓取文章")
        except Exception as e:
            flash(f"订阅源添加成功，但首次抓取失败: {str(e)}")

        return redirect(url_for("main.index"))

    return render_template("add_feed.html")


# 删除订阅源
@main_bp.route("/feed/delete/<int:feed_id>")
def delete_feed(feed_id):
    feed = Feed.query.get_or_404(feed_id)
    # 删除关联文章（可选，数据库设置了级联删除的话可省略）
    Article.query.filter_by(feed_id=feed.id).delete()
    db.session.delete(feed)
    db.session.commit()
    flash("订阅源已删除")
    return redirect(url_for("main.index"))


@main_bp.route("/feed/edit/<int:feed_id>", methods=["GET", "POST"])
def edit_feed(feed_id):
    feed = Feed.query.get_or_404(feed_id)
    if request.method == "POST":
        # 获取表单数据
        new_name = request.form.get("name")
        new_url = request.form.get("url")
        if not new_name or not new_url:
            flash("名称和URL都不能为空")
            return render_template("edit_feed.html", feed=feed)
        # 更新
        feed.name = new_name
        feed.url = new_url
        db.session.commit()
        flash("订阅源更新成功")
        return redirect(url_for("main.index"))
    # GET 请求：显示编辑表单
    return render_template("edit_feed.html", feed=feed)


# 查看某个订阅源的文章（可选）
@main_bp.route("/feed/<int:feed_id>")
def feed_articles(feed_id):
    feed = Feed.query.get_or_404(feed_id)
    page = request.args.get("page", 1, type=int)
    per_page = 10
    pagination = feed.articles.order_by(Article.published.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    articles = pagination.items
    return render_template("articles.html", feed=feed, articles=articles, pagination=pagination)


@main_bp.route("/articles")
def articles():
    # 文章列表
    # 获取当前页码，默认为 1
    page = request.args.get("page", 1, type=int)
    # 每页显示 10 条
    per_page = 10

    # 使用 paginate 代替 all()
    pagination = Article.query.order_by(Article.published.desc()).paginate(
        page=page, per_page=per_page, error_out=False  # 如果 page 超出范围，返回空列表而不是 404
    )

    # pagination.items 是当前页的文章列表
    articles = pagination.items

    return render_template("articles.html", articles=articles, pagination=pagination)


@main_bp.route("/article/<int:article_id>")
def article_detail(article_id):
    article = Article.query.get_or_404(article_id)
    # 标记为已读（可选）
    if not article.is_read:
        article.is_read = True
        db.session.commit()
    return render_template("article_detail.html", article=article)
