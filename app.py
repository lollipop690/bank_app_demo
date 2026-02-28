#run on test_flask_env
from flask import Flask,jsonify
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm, CSRFProtect
from flask_smorest import Api
from flask_jwt_extended import JWTManager
from flask_login import LoginManager
import secrets
from resources.user_blp import blp as UserBLP
from resources.cash_blp import blp as CashBLP
from resources.security_blp import blp as SecurityBLP
from db import db

import os

###Register blueprints with API

def create_app(db_url=None):
    #propagation
    app=Flask(__name__)
    app.secret_key='keane123'
    app.config['SECRET_KEY']='keane123'
    app.config['PROPAGATE_EXCEPTIONS']=True #if there is exception that occurs hidden in extension of flask, propagate it to flask app so we can see it
    #flask smorest config
    app.config['API_TITLE']='Stores REST API' #title to be in documentation
    app.config['API_VERSION']='v1' #version of API we are working on
    app.config['OPENAPI_VERSION']='3.0.3' #openapi is standard for api documentation, tell flask smorest to use 3.0.3
    app.config['OPENAPI_URL_PREFIX']='/' #tell openapi where root of api is
    app.config['OPENAPI_SWAGGER_UI_PATH']='/swagger-ui' #use swagger UI for api documentation 
    app.config['OPENAPI_SWAGGER_UI_URL']='https://cdn.jsdelivr.net/npm/swagger-ui-dist/' #import the code for the documentation here
    app.config['SQLALCHEMY_DATABASE_URI']=db_url or os.getenv("DATABASE_URL","sqlite:///bank.db") #use environment variable so can migrate database later
    #os.getenv will try to use 'database_url' for environment variable if available else will just use sqlite variables
    #using environment variable is easy way to store arbituary secrets, not good idea to store database connections strings in code
    
    #flask app is client
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
    db.init_app(app) #connect flask app to sqlalchemy
    api=Api(app)

    login_manager=LoginManager()
    login_manager.login_view='users.Login' #route to this endpoint if require authentication
    login_manager.init_app(app)
    app.config['SESSION_PERMANENT']=False

    # Bootstrap-Flask requires this line
    #bootstrap = Bootstrap5(app)
    # Flask-WTF requires this line
    #csrf = CSRFProtect(app)


    ###JWT tokens are not required for session based login only, only used API auths
    
    with app.app_context(): #will create tables before first request if it dont already exist
        import models
    #sqlalchemy knows what tables to create based on the models imported
        db.create_all()
    
    #does not need jwt token because login_manager uses session based authentication
    from models.user_model import UserModel
    @login_manager.user_loader
    def load_user(id):
        print("Loading with user id: {}".format(id))
        return UserModel.query.get(id)
    
    #register_blueprint to register blueprints for API
    api.register_blueprint(UserBLP)
    api.register_blueprint(CashBLP)
    api.register_blueprint(SecurityBLP)
    #api.register_blueprint()
    return app


