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
            cash_id=[cash.id for cash in cash_data]
            data_dict={'ID':cash_id,'Account Name':cash_name,'Value':cash_value}
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
                    print('input numbers only!')
                    return redirect('/cash/{}'.format(username)) #redirect back to cash
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


@blp.route('/cash/<username>/edit',methods=['GET','PUT','DEL','POST'])
class CashAcc(MethodView):    
    @login_required
    def get(self,username):
        if current_user.username==username:
            form_edit=forms.EditCashForm()
            form_del=forms.DelCashForm()
            cash_data=CashModel.query.filter(CashModel.user_id==username)
            cash_name=[cash.name for cash in cash_data]
            cash_value=[cash.value for cash in cash_data]
            cash_id=[cash.id for cash in cash_data]
            data_dict={'ID':cash_id,'Account Name':cash_name,'Value':cash_value}
            df=pd.DataFrame(data_dict)
            df_html=df.to_html(classes='table',index=False)
            return render_template('edit_cash.html',nameID=username,form_edit=form_edit,form_del=form_del,table=df_html)
        else:
            return redirect('/cash/{}/edit'.format(current_user.username))

    @login_required
    def post(self,username):
        if request.form.get('_edit')=='PUT': #request.form.get gets the values of the 
            print('put')
            return self.put(username)
        elif request.form.get('_delete')=='DEL':
            print('del')
            return self.delete(username)
        else:
            return {'error':'method not allowed! 405'}
        
    @login_required
    def put(self,username):
        if current_user.username==username:
            form_data=request.form
            cash_id=form_data['edit_id']
            print("input id:",cash_id)
            cash=CashModel.query.filter(CashModel.id==cash_id,CashModel.user_id==username).first()
            #Alternative
            '''
            user=UserModel.query.filter(UserModel.username==username).first()
            cash_obj=user.cash
            cash=cash_obj.filter(CashModel.id==cash_id).first()
            '''
            if cash:
                original_name=cash.name
                original_value=cash.value
                new_name=form_data['name']
                new_value=form_data['value']
                
                #new cash name
                if new_name=='':
                    new_name=original_name
                
                #new cash value
                if new_value=='':
                    new_value=original_value
                else:
                    try:
                        new_value=float(new_value)
                    except ValueError:
                        print("input numbers only!")
                        return redirect('/cash/{}/edit'.format(current_user.username))                
                cash.name=new_name
                cash.value=new_value
            else:
                print('id not found!')
                return redirect('/cash/{}/edit'.format(current_user.username))
            try:
                db.session.add(cash)
                db.session.commit()
                return redirect('/cash/{}/edit'.format(current_user.username))
            except SQLAlchemyError as e:
                abort(401,message='Input Error!')
        else:
            return redirect('/cash/{}/edit'.format(current_user.username))
    
    @login_required
    def delete(self,username):
        if current_user.username==username:
            form_data=request.form
            cash_id=form_data['del_id']
            cash=CashModel.query.filter(CashModel.id==cash_id,CashModel.user_id==username).first()
            try:
                db.session.delete(cash)
                db.session.commit()
                print('Deleted successfully!')
                return redirect('/cash/{}/edit'.format(current_user.username))
            except SQLAlchemyError as e:
                print('ID does not exist!')
                return redirect('/cash/{}/edit'.format(current_user.username))


