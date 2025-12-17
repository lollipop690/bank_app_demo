from flask import Flask,request,render_template,url_for,redirect
from flask_login import login_required,current_user
from flask.views import MethodView
from models.user_model import UserModel
from models.cash_model import CashModel
from passlib.hash import pbkdf2_sha256
from db import db
from flask_smorest import abort,Blueprint
from sqlalchemy.exc import SQLAlchemyError,IntegrityError
import pandas as pd
import forms

blp=Blueprint("cash",__name__,'cash instruments')

@blp.route('/cash/<username>',methods=['GET','POST'])
class CashAcc(MethodView):
    @login_required
    def get(self,username):
        if current_user.username==username:
            form=forms.CashForm()
            cash_data=CashModel.query.filter(CashModel.user_id==username)
            cash_name=[cash.name for cash in cash_data]
            cash_value=[cash.value for cash in cash_data]
            data_dict={'Account Name':cash_name,'Value':cash_value}
            df=pd.DataFrame(data_dict)
            df_html=df.to_html(classes='table',index=False)
            return render_template('cash.html',nameID=username,form=form,table=df_html)
        else:
            return redirect('/cash/{}'.format(current_user.username))
    @login_required
    def post(self,username):
        if current_user.username==username:
            form_data=request.form
            name=form_data['name']
            cash_name=CashModel.query.filter(CashModel.user_id==username)
            duplicate_name=False
            for cash in cash_name:
                if cash.name==name:
                    duplicate_name=True
            if duplicate_name:
                abort(401,message='No duplicates allowed!')
            else:
                try:
                    value=float(form_data['value'])
                except ValueError:
                    return "Input numbers only!"
                cash=CashModel(name=name,value=value,user_id=username)
                try:
                    db.session.add(cash)
                    db.session.commit()
                    print('added!')
                    return redirect('/cash/{}'.format(username)) #redirect back to cash
                except SQLAlchemyError as e:
                    abort(401,message='Input Error!')
        else:
            return redirect('/cash/{}'.format(current_user.username))

'''
@blp.route('/cash/<username>/edit',methods=['GET','PUT'])
class CashAcc(MethodView):    
    @login_required
    def get(self,username):
'''
