from flask_wtf import FlaskForm
from wtforms import SubmitField, BooleanField
#from wtforms import StringField, PasswordField, SubmitField, BooleanField
#from wtforms.validators import DataRequired, Length, Email, EqualTo



class DeviceOnForm(FlaskForm):    
    ison = BooleanField('Is On')
    submit = SubmitField('Submit')
