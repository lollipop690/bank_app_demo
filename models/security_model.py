from db import db

class SecurityModel(db.Model):
    __tablename__='securities'

    id=db.Column(db.Integer,primary_key=True)
    ticker=db.Column(db.String(80),unique=True,nullable=False)
    units=db.Column(db.Float,unique=False,nullable=False)
    user_id=db.Column(db.Integer,db.ForeignKey('users.username'),unique=False,nullable=False)
    user=db.relationship("UserModel",back_populates="securities") #SecurityModel.acc.name
