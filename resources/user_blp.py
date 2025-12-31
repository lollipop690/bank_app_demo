from flask import Flask, request, render_template,url_for,redirect,flash,session
from flask_login import login_required,logout_user,login_user,current_user
from flask.views import MethodView
from models.user_model import UserModel
from models.cash_model import CashModel
from models.security_model import SecurityModel
from passlib.hash import pbkdf2_sha256
from db import db
from flask_smorest import abort,Blueprint
from sqlalchemy.exc import SQLAlchemyError,IntegrityError
from flask_jwt_extended import JWTManager,jwt_required,get_jwt,create_access_token,get_jwt_identity,create_refresh_token
import forms
import pandas as pd

def dataframe(sql_obj: object):
    val_lst=[cash.value for cash in sql_obj]
    name_lst=[cash.name for cash in sql_obj]
    name_val=dict(zip(name_lst,val_lst))
    return name_val



blp=Blueprint("users",__name__,'user page')

@blp.route('/register',methods=['GET','POST'])
class Register(MethodView):

    def get(self):
        form=forms.RegistrationForm()
        return render_template('register.html',form=form) #require to GET request to the template first, url link by default is GET method
    
    def post(self):
        form_data=request.form
        username=form_data['username']
        password=pbkdf2_sha256.hash(form_data['password'])                            
        user=UserModel(username=username,password=password)
        try:
            db.session.add(user)
            db.session.commit()
            login_user(user)
            #https://tedboy.github.io/flask/interface_api.response_object.html
            return redirect('/homepage/{}'.format(username))
        except SQLAlchemyError as e:
            abort(401,message='name already exist!')

@blp.route('/login',methods=['GET','POST'])
class Login(MethodView):

    def get(self):
        form=forms.LoginForm()
        return render_template('login.html',form=form) #require to GET request to the template first, url link by default is GET method
    
    def post(self):
        form_data=request.form
        username=form_data['username']
        password=form_data['password']
        if user:=UserModel.query.filter(UserModel.username==username).first():
            if pbkdf2_sha256.verify(password,user.password):
                login_user(user)
                #on a browser, there can only be one session at a time per client
                #https://tedboy.github.io/flask/interface_api.response_object.html
                return redirect('/homepage/{}'.format(username))
            else:
                flash(message="Password is wrong!")
                return redirect(url_for('users.Login')) #name_of_blueprint.class, basically endpoint name
        else:
            flash(message="User is wrong!")
            return redirect(url_for('users.Login'))

              
@blp.route('/homepage/<username>')
class Homepage(MethodView):
    @login_required
    def get(self,username):
        print(current_user.is_authenticated)
        print(current_user.username)
        print(type(current_user))
        if current_user.username==username:
            user_data=UserModel.query.filter(UserModel.username==username).first()
            user_cash=user_data.cash #gets the related rows from the cash table
            user_cash_dict=dataframe(user_cash)
            print(user_cash_dict)
            return render_template('homepage.html',nameID=username)
        else:
            return redirect('/homepage/{}'.format(current_user.username)) #only redirect to your own account page

@blp.route('/logout')
class Logout(MethodView):
    @login_required
    def get(self):
        logout_user() #clears the user sessions and performs other logout sessions
        return redirect('/login')
