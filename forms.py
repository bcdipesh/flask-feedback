"""Form models for templates"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Email, Length


class RegistrationForm(FlaskForm):
    """User registration form"""

    username = StringField("Username", validators=[DataRequired(), Length(max=20)])
    password = PasswordField("Password", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=50)])
    first_name = StringField("First Name", validators=[DataRequired(), Length(max=30)])
    last_name = StringField("Last Name", validators=[DataRequired(), Length(max=30)])


class LoginForm(FlaskForm):
    """User login form"""

    username = StringField("Username", validators=[DataRequired(), Length(max=20)])
    password = PasswordField("Password", validators=[DataRequired()])
