import os

import click
from datetime import datetime
from flask import Flask, flash, redirect, render_template, request, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import schetime

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Custom filter
app.jinja_env.filters["schetime"] = schetime

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.secret_key = '\xca\x0c\x86\x04\x98@\x02b\x1b7\x8c\x88]\x1b\xd7"+\xe6px@\xc3#\\'

# 配置数据库
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.root_path, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 关闭对模型修改的监控
# 在扩展类实例化前加载配置
db = SQLAlchemy(app)

class Record(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    create_at = db.Column(db.DateTime, default=datetime.now())
    title = db.Column(db.Text, nullable=False)
    tag = db.Column(db.String(20), nullable=False)
    content = db.Column(db.Text, nullable=False)


@app.route('/error')
def error(message, error_code):
    return render_template("error.html", message=message.upper(), error_code=error_code)

@app.route('/home')
def home():
    session.clear()
    session["user_id"] = "0"
    records = Record.query.filter(Record.tag!='haha')
    return render_template("home.html", records=records)

@app.route('/')
def portal():
    session.clear()
    return render_template("layout.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    session.clear()
    if request.method == "GET":
        return render_template("login.html")
    else:
        # TODO
        return redirect("/home")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    session.clear()
    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Miss any of the three requirments: username, password, confirmation
        if not username or not password or not confirmation:
            return error("each of the fields is required", 400)

        # password and confirmation don't match
        elif password != confirmation:
            return error("password and confirmation do not match", 400)

        # information OK
        else:
            return redirect("/home")

    else:
        return render_template("register.html")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


# Fundtions
@app.route('/add', methods=["GET", "POST"])
def add():
    title = request.form.get('title')
    tag = request.form.get('tag')
    content = request.form.get('content')

    # The information is completed
    if title and tag and content:
        record = Record(title=title, tag=tag, content=content)
        db.session.add(record)
        db.session.commit()
    return render_template("add.html")

@app.route('/diary')
def diary():
    records = Record.query.filter_by(tag='diary')
    return render_template("diary.html", records=records)

@app.route('/notes')
def notes():
    records = Record.query.filter_by(tag='notes')
    return render_template("notes.html", records=records)

@app.route('/saying')
def saying():
    records = Record.query.filter_by(tag='saying')
    return render_template("saying.html", records=records)