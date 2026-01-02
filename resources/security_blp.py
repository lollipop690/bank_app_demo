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
from yfinance_fn import check_validity
import pandas as pd

blp=Blueprint("security",__name__,'security instruments')

@blp.route('/securities/<username>',methods=['GET','POST'])
class SecAcc(MethodView):
    
    @login_required
    def get(self,username):
        if current_user.username==username:
            form=forms.SecurityForm()

            #display table 
            sec_data=SecurityModel.query.filter(SecurityModel.user_id==username)
            sec_ticker=[sec.ticker for sec in sec_data]
            sec_units=[sec.units for sec in sec_data]
            sec_id=[sec.id for sec in sec_data]
            data_dict={'ID':sec_id,'Account Name':sec_ticker,'Value':sec_units}
            df=pd.DataFrame(data_dict)
            df_html=df.to_html(classes='table',index=False)
            
            return render_template('security.html',nameID=username,form=form,table=df_html)
        else:
            return redirect('/securities/{}'.format(current_user.username))
    
    @login_required
    def post(self,username):
        if current_user.username==username:
            form_data=request.form
            ticker=form_data['ticker']
            check=check_validity(ticker)
            if check:
                try:
                    units=float(form_data['units'])
                except ValueError:
                    print("Must be in numbers!")
                    return redirect('/securities/{}'.format(current_user.username))
                security=SecurityModel(ticker=ticker,units=units,user_id=username)
                try:
                    db.session.add(security)
                    db.session.commit()
                    print('added!')
                    return redirect('/securities/{}'.format(current_user.username))
                except SQLAlchemyError:
                    print('Ticker already exist!')
                    return redirect('/securities/{}'.format(current_user.username))
            else:
                print('Invalid Ticker')
                return redirect('/securities/{}'.format(current_user.username))
        else:
            return redirect('/securities/{}'.format(current_user.username))
        
@blp.route('/securities/<username>/edit',methods=['GET','POST','PUT','DEL'])
class EditSecAcc(MethodView):
    
    @login_required
    def get(self,username):
        if current_user.username==username:
            edit_form=forms.EditSecForm()
            del_form=forms.DelCashForm()
            
            #display table 
            sec_data=SecurityModel.query.filter(SecurityModel.user_id==username)
            sec_ticker=[sec.ticker for sec in sec_data]
            sec_units=[sec.units for sec in sec_data]
            sec_id=[sec.id for sec in sec_data]
            data_dict={'ID':sec_id,'Account Name':sec_ticker,'Value':sec_units}
            df=pd.DataFrame(data_dict)
            df_html=df.to_html(classes='table',index=False)
            
            return render_template('edit_securities.html',nameID=username,edit_form=edit_form,del_form=del_form,table=df_html)
        else:
            return redirect('/securities/{}/edit'.format(current_user.username))
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
            sec_id=form_data['edit_id']
            new_units=form_data['units']
            security=SecurityModel.query.filter_by(SecurityModel.id==sec_id,SecurityModel.user_id==username).first()
            
            if security:
                original_units=security.units
                #new units amount
                if new_units=='':
                    new_units==original_units
                else:
                    try:
                        new_units=float(new_units)
                    except ValueError:
                        print("input numbers only!")
                        return redirect('/cash/{}/edit'.format(current_user.username)) 
                
                security.units=new_units
                try:
                    db.session.add(security)
                    db.session.commit()
                    return redirect('/securities/{}/edit'.format(current_user.username))
                except SQLAlchemyError as e:
                    print('sqlalchemy error raised!')
                    return redirect('/securities/{}/edit'.format(current_user.username))
            else:
                print('id does not exist!')
                return redirect('/securities/{}/edit'.format(current_user.username))

        else:
            return redirect('/securities/{}/edit'.format(current_user.username))
        
    @login_required
    def delete(self,username):
        if current_user.username==username:
            form_data=request.form
            sec_id=form_data['del_id']
            security=SecurityModel.query.filter_by(SecurityModel.id==sec_id,SecurityModel.user_id==username).first()
            if security:
                try:
                    db.session.delete(security)
                    db.session.commit()
                    return redirect('/securities/{}/edit'.format(current_user.username))
                except SQLAlchemyError as e:
                    print('sqlalchemy error raised!')
                    return redirect('/securities/{}/edit'.format(current_user.username))
            else:
                print('id does not exist!')
                return redirect('/securities/{}/edit'.format(current_user.username))
        else:
            return redirect('/securities/{}/edit'.format(current_user.username))
        
