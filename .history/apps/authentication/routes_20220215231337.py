# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""






from flask_paginate import Pagination,get_page_args
from flask import render_template, redirect, request, url_for,Flask
from flask_login import (
    current_user,
    login_user,
    logout_user
)
import os
import csv
import pandas as pd

app=Flask(__name__)
from apps import db, login_manager
from apps.authentication import blueprint
from apps.authentication.forms import LoginForm, CreateAccountForm
from apps.authentication.models import Users

from apps.authentication.util import verify_pass


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
app.config["UPLOAD_FOLDER"] = "F:/kienThucTrenTruong/Python/LearnPython/apps/static/upload-file"
@blueprint.route('/upload-file',methods=["POST","GET"])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        #filename=file.filename
        # file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
     
        data = pd.read_csv(file)
        print(data.to_dict())
        reader = csv.DictReader(data)
       # print(reader)
        results=[]
        for row in reader:
            ##print(row)
            results.append(dict(row))
        fieldnames = [key for key in results[0].keys()]
        ##print(results)
        return render_template('home/manipulating-file.html', results=results,fieldnames=fieldnames, len=len)
    return render_template('home/manipulating-file.html')
# endregion

#Method
def get_users(offset=0, per_page=10):
    users = Users.query.all()
    return users[offset: offset + per_page]

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
