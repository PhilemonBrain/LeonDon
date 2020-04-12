



class PaymentForm(FlaskForm):
    amount = IntegerField('Amount', validators=[DataRequired()])
    date = DateField('Date Of Payment')
    submit = SubmitField('Add Payment')