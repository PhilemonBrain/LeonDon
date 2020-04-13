from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import ValidationError, DataRequired, EqualTo, Email
from flask_wtf import FlaskForm
from ldon.models import Staff


class RequestResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request password reset')

    def validate_email(self, email):
        staff = Staff.query.filter_by(email=email.data).first()
        if staff is None:
            raise ValidationError('No Account Found')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField('Reset Password')
