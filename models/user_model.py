from db import db
from flask_login import UserMixin

class UserModel(UserMixin,db.Model):
    __tablename__='users'
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(30),unique=True,nullable=False)
    password=db.Column(db.String(200),unique=False,nullable=False)
    cash=db.relationship('CashModel',back_populates='user',lazy='dynamic')
    securities=db.relationship('SecurityModel',back_populates='user',lazy='dynamic')

    #cash and securities are now related via users.username
    '''
    @property #overriding the inherrited attributes of UserMixin, using a getter property decorator
    def is_authenticated(self):
        if 
    '''