from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, DateField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_login import current_user
from ldon.models import Staff, Client


class RegistrationForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    date = DateField('Account Opens')
    amount = IntegerField('Loan Amount', validators=[DataRequired()])
    phone_number = IntegerField('Phone Number', validators=[DataRequired(), Length(min=11, max=11, message='Must be 11 characters long')])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo("password")])
    picture = FileField('Upload Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Register')

    def validate_username(self, username):
        client = Client.query.filter_by(username=username.data).first()
        if client:
            raise ValidationError('This Username has been used to open an account. Please choose a different email')

    def validate_email(self, email):
        client = Client.query.filter_by(email=email.data).first()
        if client:
            raise ValidationError('This Email has been used to open an account. Please choose a different email')


class UpdateAccountForm(FlaskForm):
    full_name = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    def validate_username(self, full_name):
        if current_user.full_name != full_name.data:
            staff = Staff.query.filter_by(full_name=full_name.data).first()
            if staff:
                raise ValidationError('This Email has already been taken. Please choose a different one')

    def validate_email(self, email):
        if current_user.email != email.data:
            staff = Staff.query.filter_by(email=email.data).first()
            if staff:
                raise ValidationError('This Email has already been taken. Please choose a different one')


class RegistrationForm2(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    date = DateField('Account Opens')
    amount = IntegerField('Loan Amount', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo("password")])
    picture = FileField('Upload Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Register')

    def validate_username(self, username):
        client = Client.query.filter_by(username=username.data).first()
        if client:
            raise ValidationError('This Username has been used to open an account. Please choose a different email')

    def validate_email(self, email):
        client = Client.query.filter_by(email=email.data).first()
        if client:
            raise ValidationError('This Email has been used to open an account. Please choose a different email')
