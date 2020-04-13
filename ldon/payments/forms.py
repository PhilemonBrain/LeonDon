from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField, DateField
from wtforms.validators import DataRequired


class PaymentForm(FlaskForm):
    amount = IntegerField('Amount', validators=[DataRequired()])
    date = DateField('Date Of Payment')
    submit = SubmitField('Add Payment')
