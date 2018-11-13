#!/usr/bin/env python3
# encoding:utf-8
import os
from datetime import datetime

from flask import Flask, request, render_template, url_for, flash, Blueprint
from flask_bootstrap import Bootstrap
from sqlalchemy import desc
from werkzeug.utils import secure_filename, redirect
import json
from flask_login import current_user, login_required
from my_utils import my_secure_filename, hgihtlight_word
from data_model import db, Article, User, Tag, Message, Link
from auth import login_manager
import config_t
from auth import auth as auth_blueprint
import commonmark
import v2ray_config

app = Flask(__name__)
app.config.from_object(config_t)
bootstrap = Bootstrap(app)
db.init_app(app)
login_manager.init_app(app)
app.register_blueprint(auth_blueprint)
app.jinja_env.globals.update(hgihtlight_word=hgihtlight_word)


@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404

# @app.route("/utils")
# def utils():
#    tag = Tag.query.all()
#    for a in tag:
#        print(a.name)2
#        tagmap = Tagmap.query.filter_by(tag_id=a.id).all()
#        print(len(tagmap))
#        for ar in tagmap:
#            print(ar.article)
#            print(ar.article.title)
#
#    return render_template('utils.html')

def get_tag_dict():
    tag_dict = {}
    tags = Tag.query.all()
    for tag in tags:
        tag_dict[tag.name] = (tag.id, len(tag.articles.all()))
    return tag_dict


def root_required(func):
    '''
    装饰器，有些操作只有我能执行，验证current_user为管理员
    '''

    def access_is_0(*args, **kwargs):
        if current_user.access == 0:
            func(*args, **kwargs)
        else:
            # flash("You have no permission to access this page")
            # TODO: diffrent call from diffrent path
            return "ERROR PERMISSION"

    return access_is_0


@app.route('/')
def index():
    url_page = request.args.get("page", 1, type=int)
    url_tag = request.args.get("tag", type=int)
    pagination = None
    if url_tag:
        c_tag = Tag.query.filter_by(id=url_tag).first()
        pagination = c_tag.articles.order_by(desc(Article.time)).paginate(url_page,
                                                                          per_page=app.config['POSTS_PER_PAGE'],
                                                                          error_out=True)
    else:
        pagination = Article.query.order_by(desc(Article.time)).paginate(url_page,
                                                                         per_page=app.config['POSTS_PER_PAGE'],
                                                                         error_out=True)
    articles = pagination.items
    return render_template('index.html', articles=articles, pagination=pagination, tag_dict=get_tag_dict(),
                           args=request.args)


@app.route('/up', methods=['GET', 'POST'])
def my_upload():
    if request.method == "POST":
        f = request.files['inputfile']
        if os.name == "posix":
            upload_path = os.path.join("/myvps", 'upload', my_secure_filename(f.filename))
        else:
            upload_path = os.path.join("e:\\tmp", '', my_secure_filename(f.filename))

        f.save(upload_path)
        return redirect(url_for('my_upload'))
    return render_template('up.html')


@app.route('/write_article', methods=['GET'])
@login_required
def write_article():
    return render_template('write_article.html')


@app.route('/post_article', methods=['POST'])
@login_required
def post_article():
    if current_user.access != 0:
        # flash("当前用户没有权限发布文章！")
        return "Cant access!"
    try:
        article_info = json.loads(str(request.get_data(), encoding="utf-8"))
        article = Article(
            author=current_user.id,
            time=datetime.now(),
            title=article_info["title"],
            text=article_info["main"])
        if len(article_info["title"]) == 0:
            return "Has No Title!"
        new_list = map(str.strip, article_info["tags"])
        db.session.add(article)
        for i in new_list:
            if len(i) == 0:
                continue
            tag = Tag.query.filter_by(name=i).first()
            if tag:
                tag.articles.append(article)
                pass
            else:
                new_tag = Tag(name=i)
                db.session.add(new_tag)
                new_tag.articles.append(article)
        db.session.commit()
    except Exception as e:
        print(e)
        db.session.rollback()
        return "Unknown error!"
    return "OK"


@app.route('/modify_article/<id>', methods=['POST'])
@login_required
def modify_article(id):
    if current_user.access != 0:
        # flash("当前用户没有修改文章！")
        return "Cant access!"
    try:
        article = Article.query.get(int(id))
        article_info = json.loads(str(request.get_data(), encoding="utf-8"))
        article.text = article_info["main"]
        article.title = article_info["title"]
        if len(article_info["title"]) == 0:
            return "Has No Title!"
        # todo handle tags
        # new_list = map(str.strip, article_info["tags"])
        # for i in new_list:
        #     if len(i) == 0:
        #         continue
        #     tag = Tag.query.filter_by(name=i).first()
        #     if tag:
        #         if not article in tag.articles:
        #             tag.articles.append(article)
        #     else:
        #         new_tag = Tag(name=i)
        #         db.session.add(new_tag)
        #         new_tag.articles.append(article)
        db.session.commit()
    except Exception as e:
        print(e)
        db.session.rollback()
        return "Unknown error!"
    return "OK"


@app.route('/select_tags')
def select_tags():
    rs = []
    all = Tag.query.all()
    for i in all:
        rs.append(i.name)
    return json.dumps(rs)


@app.route("/article/<id>")
def a_article(id):
    article = Article.query.get(int(id))
    if not article: app.abort(404)
    parser = commonmark.Parser()
    ast = parser.parse(article.text)
    renderer = commonmark.HtmlRenderer()
    html = renderer.render(ast)

    article_dict = {
        "title": article.title,
        "time": str(article.time),
        "text": html,
        "author": article.user.name
    }

    return render_template("article.html", id=id, tag_dict=get_tag_dict(), article_dict=article_dict)


@app.route("/article_info/<id>")
def a_article_info(id):
    article = Article.query.get(int(id))
    article_json = {
        "title": article.title,
        "time": str(article.time),
        "text": article.text,
        "author": article.user.name
    }
    return json.dumps(article_json)


@app.route("/article/delete/<id>")
@login_required
def del_article(id):
    if current_user.access != 0:
        return "Cant access!"
    article = Article.query.get(int(id))
    db.session.delete(article)
    db.session.commit()
    flash("已删除一篇文章！")
    return redirect(url_for("index"))


@app.route("/article/modify/<id>")
@login_required
def modify_articcle(id):
    if current_user.access != 0:
        return "Cant access!"
    article = Article.query.get(int(id))
    return render_template('write_article.html', article=article)


@app.route("/search")
def search_article():
    k = request.args.get("keyword")
    if len(k) == 0:
        return redirect(url_for("index"))
    ar = Article.query.filter(Article.title.like("%" + k + "%"))
    pagination = ar.order_by(desc(Article.time)).paginate(1, per_page=1024, error_out=True)
    return render_template('index.html', articles=pagination.items, pagination=pagination, tag_dict=get_tag_dict(),
                           args=request.args, search_keyword=k)


@app.route("/utils")
def utils_src():
    return redirect(url_for("utils", wh="up"))


@app.route("/utils/<wh>")
def utils(wh):
    if wh == "message":
        pass
    elif wh == "links":
        all = Link.query.all()
        return render_template(wh + ".html", util_id=wh, links=all)
    return render_template(wh + ".html", util_id=wh)


@app.route("/add_mess", methods=['POST'])
def add_mess():
    mess_info = json.loads(str(request.get_data(), encoding="utf-8"))
    mess = Message(
        message=mess_info['mess'],
        time=datetime.now()
    )
    if mess.message == "":
        app.abort(500)
        return
    db.session.add(mess)
    db.session.commit()
    return "OK"


@app.route("/add_links", methods=['POST'])
@login_required
def add_links():
    link_info = json.loads(str(request.get_data(), encoding="utf-8"))
    link = Link(
        title=link_info['title'],
        link=link_info['addr']
    )
    if link.title == "" or link.link == "":
        app.abort(500)
        return
    db.session.add(link)
    db.session.commit()
    return "OK"


@app.route("/get_mess")
def get_mess():
    if current_user.access != 0:
        app.abort(500)
    n = int(request.args.get("n"))
    if n == None or n == 0:
        n = 10
    all = Message.query.order_by(desc(Message.id)).all()
    rs = []
    for i, j in enumerate(all):
        if i > n: break
        rs.append(j.message)
    return json.dumps(rs)


@app.route("/gen_v2ray_config", methods=['POST'])
def gen_v2ray_config():
    v_info = json.loads(str(request.get_data(), encoding="utf-8"))
    rs = v2ray_config.get_v2ray_config(v_info)
    (use_c, use_s, use_re, conf_c, conf_s, data_re) = rs
    conf_r = ""
    if data_re[0] == 1:
        conf_r = render_template("nginx.conf", port=data_re[1], server_name=data_re[2], path=data_re[3],
                                 be_proxy=data_re[4],tls_config=data_re[5],ssl=data_re[6])
    elif data_re[0] == 2:
        conf_r = render_template("Caddyfile-ws", domain=data_re[1], tls=data_re[2], path=data_re[3],
                                 be_proxy=data_re[4])
    elif data_re[0] == 3:
        conf_r = render_template("Caddyfile-h2", domain=data_re[1], path=data_re[2], be_proxy=data_re[3],
                                 host_domain=data_re[4])
    else:
        use_re = False

    if not use_c:
        conf_c = "N/A"
    if not use_s:
        conf_s = "N/A"
    if not use_re:
        conf_r = "N/A"

    config = {
        "c": conf_c,
        "s": conf_s,
        "r": conf_r
    }
    return json.dumps(config)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000, debug=True)
