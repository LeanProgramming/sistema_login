import email
from flask_wtf import FlaskForm
from wtforms import PasswordField, EmailField, SubmitField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    submit = SubmitField('Confirmar')