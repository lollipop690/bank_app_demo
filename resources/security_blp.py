from flask import Flask,request,render_template,url_for,redirect,Response,stream_with_context
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
from redis_setup import start_stream,get_prices_for_tickers
import json
import redis
import time
import requests as rq

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
    
            rows = [
                {'id': i, 'ticker': t, 'units': u}
                for i, t, u in zip(sec_id, sec_ticker, sec_units)
            ]
            
            return render_template('security.html',nameID=username,form=form,rows=rows)
        else:
            return redirect('/securities/{}'.format(current_user.username))
    
    @login_required
    def post(self,username):
        if current_user.username==username:
            form_data=request.form
            ticker=form_data['ticker']
            check=check_validity(ticker)
            security_existing=SecurityModel.query.filter(SecurityModel.user_id==username,SecurityModel.ticker==ticker).first()
            if security_existing:
                duplicate=True
            else:
                duplicate=False
            if not duplicate:
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
                        try:
                            start_stream([ticker])
                        except redis.ConnectionError:
                            print("Redis connection error")
                        print('added!')
                        return redirect('/securities/{}'.format(current_user.username))
                    except SQLAlchemyError:
                        print('Error!')
                        return redirect('/securities/{}'.format(current_user.username))
                else:
                    print('Invalid ticker!')
                    return redirect('/securities/{}'.format(current_user.username))
            else:
                print('No duplicates')
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
            
            return render_template('edit_securities.html',nameID=username,form_edit=edit_form,form_del=del_form,table=df_html)
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
            security=SecurityModel.query.filter(SecurityModel.id==sec_id,SecurityModel.user_id==username).first()
            
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
            security=SecurityModel.query.filter(SecurityModel.id==sec_id,SecurityModel.user_id==username).first()
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
        
@blp.route('/securities/<username>/stream',methods=['GET'])
class StreamPrices(MethodView):
    @login_required
    def get(self,username):
        if current_user.username==username:
            sec_data = SecurityModel.query.filter(SecurityModel.user_id==username) #get all rows with this username
            #no possiblity for duplicate tickers for each username because replicates are not allowed to be added
            tickers = [sec.ticker for sec in sec_data]

            def stream_prices():
                while True:
                    prices = get_prices_for_tickers(tickers)
                    #yield f"data: {json.dumps(prices)}\n\n"
                    yield json.dumps(prices) + '\n' #returns an iterable of objects
                    time.sleep(1.5)
            
            return Response(stream_with_context(stream_prices()),mimetype = 'text/event-stream')

        else:
            return redirect('/securities/{}/stream'.format(current_user.username))