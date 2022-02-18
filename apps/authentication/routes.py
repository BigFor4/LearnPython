# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""





import flask
from tablib import Dataset
from flask_paginate import Pagination,get_page_args
from flask import render_template, redirect, request, url_for,Flask,flash
from flask_login import (
    current_user,
    login_user,
    logout_user
)
import pygal
import re
import pandas as pd
from collections.abc import Iterable
app=Flask(__name__)
from apps import db, login_manager
from apps.authentication import blueprint
from apps.authentication.forms import LoginForm, CreateAccountForm
from apps.authentication.models import Users
import os
from apps.authentication.util import verify_pass


# uploads folder should be exesit
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
ALLOWED_EXTENSIONS = {'CSV','csv'}
@blueprint.route('/')
def route_default():
    return redirect(url_for('authentication_blueprint.login'))


# Login & Registration

@blueprint.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm(request.form)
    if 'login' in request.form:

        # read form data
        username = request.form['username']
        password = request.form['password']

        # Locate user
        user = Users.query.filter_by(username=username).first()

        # Check the password
        if user and verify_pass(password, user.password):
            login_user(user)
            return redirect(url_for('authentication_blueprint.route_default'))

        # Something (user or pass) is not ok
        return render_template('accounts/login.html',
                               msg='Wrong user or password',
                               form=login_form)

    if not current_user.is_authenticated:
        return render_template('accounts/login.html',
                               form=login_form)
    return redirect(url_for('home_blueprint.index'))


@blueprint.route('/register', methods=['GET', 'POST'])
def register():
    create_account_form = CreateAccountForm(request.form)
    if 'register' in request.form:

        username = request.form['username']
        email = request.form['email']

        # Check usename exists
        user = Users.query.filter_by(username=username).first()
        if user:
            return render_template('accounts/register.html',
                                   msg='Username already registered',
                                   success=False,
                                   form=create_account_form)

        # Check email exists
        user = Users.query.filter_by(email=email).first()
        if user:
            return render_template('accounts/register.html',
                                   msg='Email already registered',
                                   success=False,
                                   form=create_account_form)

        # else we can create the user
        user = Users(**request.form)
        db.session.add(user)
        db.session.commit()

        return render_template('accounts/register.html',
                               msg='User created please <a href="/login">login</a>',
                               success=True,
                               form=create_account_form)

    else:
        return render_template('accounts/register.html', form=create_account_form)


@blueprint.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('authentication_blueprint.login'))

#region
@blueprint.route('/profile')
def get_profile():
    return render_template("/accounts/profile.html",user=current_user)

@blueprint.route('/manage-user')
def getListUser():
    page, per_page, offset = get_page_args(page_parameter='page',per_page_parameter='per_page')
    total = len(Users.query.all())
    pagination_users = get_users(offset=offset, per_page=per_page)
    pagination = Pagination(page=page, per_page=per_page, total=total,css_framework='bootstrap4')
    return render_template('users/manage-user.html',users=pagination_users
    ,page=page,per_page=per_page,pagination=pagination)

@blueprint.route('/save-details',methods=["POST","GET"])
def saveDetails():
    msg = "msg"
    if(request.method=="POST"):
        try:
            username = request.form["username"]
            email=request.form["email"]
            password=request.form["password"]
            msg ="User successfully Added"
            user = Users.query.filter_by(username=username).first()
            if user:
                msg="User registered"
                return render_template("home/success.htm",msg=msg)
            # user = {id : db.Column(db.Integer, primary_key=True),
            # username:username,email:email,password:password}
            user = Users(**request.form)
            db.session.add(user)
            db.session.commit()
        except:
            msg="We can't add the user to the list"
        finally:
            return render_template("home/success.htm",msg=msg)

@blueprint.route('/manage-user/delete-record',methods=["POST"])
def deleterecord():  
    userArray=request.form["userIdArray"]
    user=Users.query.filter_by(id=userArray).first()
    if user:
        db.session.delete(user)
        db.session.commit()
        return redirect("/manage-user")
    
   
    return redirect("/manage-user")


@blueprint.route('/manage-user/user/<int:id>')
def delete_user(id):
    user = Users.query.filter_by(id=id).first()
    if user:
        db.session.delete(user)
        db.session.commit()
        return redirect("/manage-user")
    return redirect("/manage-user")

@blueprint.route('/manage-user/user/edit',methods=["POST"])
def edit_user():
    id=request.form['id']
    email=request.form['email']
    username=request.form['username']
    user=db.session.query(Users).get(id)
    if user:
        user.username=username
        user.email=email
        db.session.commit()
    return redirect("/manage-user")


# ## thao tác csv
# @blueprint.route('/upload-file',methods=["GET"])
# def upload_file():
#     return render_template('manipulating-file.html')
app.config["UPLOAD_FOLDER"] = "E:/python/LearnPython/apps/static/upload-file"
@blueprint.route('/upload-file',methods=["POST","GET"])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        data = pd.read_csv(file)
        print(data.to_html())
        return render_template('home/manipulating-file.html', results=data.to_html())
    return render_template('home/manipulating-file.html')




file_name=""
@blueprint.route('/chart')
def chart():
    global header
    global data
    global option
    file_name="/csv/analyze.csv"
    with open(file_name,"r") as line:
        dataset = Dataset()
        dataset.csv = line.read()
    data = dataset.html
    option = ["mean","sum","max","min","count","median","std","var"]
    header = open(file_name).readline().rstrip()
    print(header)
    if "," in header:
        header=open(file_name).readline().rstrip().split(",")
    elif " " in header:
        header=open(file_name).readline().rstrip().split(" ")
    elif "." in header:
        header=open(file_name).readline().strip().split(".")
    else:
        flask("that header of file not support split")
        return redirect("/")
    return render_template("/charts/show.html",lines=data,option=option,header=header)

@blueprint.route('/analyze')
def analyze():
    name = request.args.get("myselect")
    option_var = request.args.get("myoption")

    if name not in header:
        flash("please select the header and option")
        print("please select the header and option")
        return redirect("/")
    elif option_var not in option:
        flash("option not found ")
        print("option not found")
        return redirect("/")
    file_name="E:/python/LearnPython/csv/analyze.csv"
    df = pd.read_csv(file_name)
    try:
        if option_var == "mean":
            set_data = df[name].mean()
        elif option_var == "sum":
            set_data = df[name].sum()
        elif option_var == "max":
            set_data = df[name].max()
        elif option_var == "count":
            set_data = df[name].count()
        elif option_var == "std":
            set_data = df[name].std()
        elif option_var == "var":
            set_data = df[name].var()
        elif option_var == "min":
            set_data = df[name].min()
    except:
        flash("pleas make sure use the option with the valid header you can't use some option with string value !")
        print("pleas make sure use the option with the valid header you can't use some option with string value !")
        return redirect("/")

    imported_data = Dataset().load(open(file_name).read())
    data = imported_data[name]
    new_list = []
    for d in data:
        try:
            if d.isdigit():
                new_list.append(int(d))
            elif type(d) == str:
                new_list.append(float(d))
        except:
            flash("this option only for Number")
            return redirect("/")

    graph = pygal.Line()
    graph.title = "Full customization option For " + str(name)
    graph.x_labels = []
    graph.add(name, new_list)
    graph_data = graph.render_data_uri()

    return render_template("/charts/analyze.html", set_data=set_data, option_var=option_var, name=name, graph_data=graph_data)
# endregion

#Method
def get_users(offset=0, per_page=10):
    users = Users.query.all()
    return users[offset: offset + per_page]

def get_emails_formfile(file):
    emails = re.findall("([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)",file)
    return emails

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# def fig_to_base64(fig):
#     img = io.BytesIO()
#     fig.savefig(img, format='png',
#                 bbox_inches='tight')
#     img.seek(0)

#     return base64.b64encode(img.getvalue())


#endMethod

# Errors

@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template('home/page-403.html'), 403


@blueprint.errorhandler(403)
def access_forbidden(error):
    return render_template('home/page-403.html'), 403


@blueprint.errorhandler(404)
def not_found_error(error):
    return render_template('home/page-404.html'), 404


@blueprint.errorhandler(500)
def internal_error(error):
    return render_template('home/page-500.html'), 500
