from db import db

class CashModel(db.Model):
    __tablename__='cash'

    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(100),nullable=False,unique=False)
    value=db.Column(db.Float,nullable=False,unique=False)
    user_id=db.Column(db.String,db.ForeignKey('users.username'),nullable=False,unique=False)
    user=db.relationship('UserModel',back_populates='cash')