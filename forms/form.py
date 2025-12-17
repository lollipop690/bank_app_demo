from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField,IntegerField
from wtforms.validators import DataRequired

class RegistrationForm(FlaskForm):
    username=StringField('Input name:')
    password=PasswordField('Password:')
    submit=SubmitField('Submit')

class LoginForm(FlaskForm):
    username=StringField('Input name:')
    password=PasswordField('Password:')
    submit=SubmitField('Submit')

class CashForm(FlaskForm):
    name=StringField('Name of cash asset: ')
    value=StringField('Value of asset: ')
    submit=SubmitField('Submit')

class SecurityForm(FlaskForm):
    ticker=StringField('Ticker: ')
    units=StringField('Units: ')
    submit=SubmitField('Submit')