from flask import Flask,request,render_template,url_for,redirect
from flask.views import MethodView
from models.user_model import UserModel
from models.security_model import SecurityModel
from passlib.hash import pbkdf2_sha256
from db import db
from flask_smorest import abort,Blueprint
from schemas import PlainUserSchema,PlainCashSchema,CashSchema
from sqlalchemy.exc import SQLAlchemyError,IntegrityError
from flask_jwt_extended import JWTManager,jwt_required,get_jwt


blp=Blueprint("security",__name__,'security instruments')

@blp.route('/securities/<username>',methods=['GET','POST'])
class SecAcc(MethodView):
    def get(self,username):
        print("not ready yet!")
        return render_template('security.html',nameID=username)