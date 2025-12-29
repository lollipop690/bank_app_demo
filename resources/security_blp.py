from flask import Flask,request,render_template,url_for,redirect
from flask.views import MethodView
from models.user_model import UserModel
from models.security_model import SecurityModel
from passlib.hash import pbkdf2_sha256
from db import db
from flask_smorest import abort,Blueprint
from sqlalchemy.exc import SQLAlchemyError,IntegrityError
from flask_login import login_required,current_user
import forms
import yfinance as yf


blp=Blueprint("security",__name__,'security instruments')

@blp.route('/securities/<username>',methods=['GET','POST'])
class SecAcc(MethodView):
    
    def get(self,username):
        if current_user.username==username:
            form=forms.SecurityForm()
            '''
            cash_data=CashModel.query.filter(CashModel.user_id==username)
            cash_name=[cash.name for cash in cash_data]
            cash_value=[cash.value for cash in cash_data]
            cash_id=[cash.id for cash in cash_data]
            data_dict={'ID':cash_id,'Account Name':cash_name,'Value':cash_value}
            df=pd.DataFrame(data_dict)
            df_html=df.to_html(classes='table',index=False)
            '''
            return render_template('security.html',nameID=username,form=form)
        else:
            return redirect('/securities/{}'.format(current_user.username))
    
    def post(self,username):
        if current_user.username==username:
            form_data=request.form
            
        else:
            return redirect('/securities/{}'.format(current_user.username))