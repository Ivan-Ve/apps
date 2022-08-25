from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, URL
 
##WTForm
class CreatePostForm(FlaskForm):
  title = StringField("Enter The Word", validators=[DataRequired()])
  submit = SubmitField("Submit Request")

## Register form
class RegisterForm(FlaskForm):
  email = StringField("Email", validators=[DataRequired()])
  password = PasswordField("Password", validators=[DataRequired()])
  name = StringField("Name", validators=[DataRequired()])
  submit = SubmitField("Sign Me Up!")

## Login form
class LoginForm(FlaskForm):
  email = StringField("Email", validators=[DataRequired()])
  password = PasswordField("Password", validators=[DataRequired()])
  submit = SubmitField("Login")