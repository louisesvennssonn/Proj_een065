import datetime

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, IntegerField, DateTimeField, DecimalField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from stock_analysis.models import User, Stock, Analysis


# WTForms fields: https://wtforms.readthedocs.io/en/2.3.x/fields/
# WTForms HTML5 fields: https://wtforms.readthedocs.io/en/2.3.x/fields/#module-wtforms.fields.html5
# WTForms validators: https://wtforms.readthedocs.io/en/2.3.x/validators/


class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(),  # this field must be filled
                                       Length(min=2, max=20)  # the username must have 2-20 characters
                                       ]
                           )
    email = EmailField('Email',
                       validators=[DataRequired(),  # the user must fill this field
                                   Email()  # validate as an email
                                   ]
                       )
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(),  # user must fill the `confirm password`
                                                 EqualTo('password')  # the value here must be equal to the `password`
                                                 ]
                                     )
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:  # if a user exists with this username, then you cannot create a second user using it
            raise ValidationError('This username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:  # if a user exists with this email, then you cannot create a second user using it
            raise ValidationError('This email is taken. Please choose a different one.')


class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    # BooleanField renders a checkbox field
    # doc: https://www.w3schools.com/tags/att_input_type_checkbox.asp
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


# this form is quite similar to the RegistrationForm
class UpdateAccountForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = EmailField('Email',
                       validators=[DataRequired(), Email()])

    # FileField creates a field where the user can upload a file
    # doc: https://www.w3schools.com/tags/att_input_type_file.asp
    # note that the form tag must use the enctype: https://www.w3schools.com/tags/att_form_enctype.asp
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')


class StockForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=1, max=20)])
    number_of_shares = IntegerField('Number of shares', validators=[DataRequired()])
    ticker = StringField('Ticker (4 letters)', validators=[DataRequired(), Length(min=4, max=4)])
    create = SubmitField('Create')


class AnalysisForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=1, max=50)])
    content = TextAreaField('Content', validators=[DataRequired(), Length(min=1, max=600)])
    price = DecimalField('Price', validators=[DataRequired()], places=2)
    earnings = DecimalField('Earnings', validators=[DataRequired()], places=2)
    p_e = DecimalField('P_E', validators=[DataRequired()], places=2)
    market_cap = DecimalField('Market cap', validators=[DataRequired()], places=2)
    submit = SubmitField('Submit')


class DiagramForm(FlaskForm):
    price = DecimalField('Price', validators=[DataRequired()], places=2)
    submit = SubmitField('Add')

