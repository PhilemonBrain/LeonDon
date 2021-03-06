from flask import Blueprint, render_template, redirect, flash, url_for
from ldon.models import Client, Payments
from .forms import PaymentForm
from flask_login import login_required
from ldon import db


payments_blueprint = Blueprint('Payments', __name__)


@payments_blueprint.route('/client/<int:id>/add_payment', methods=['POST', 'GET'])
@login_required
def add_payment(id):
    form = PaymentForm()
    client = Client.query.get_or_404(id)
    if form.validate_on_submit():
        amount_paid = form.amount.data
        if amount_paid <= client.loan_balance:
            interest_paid = amount_paid / 10
            principal_paid = amount_paid - interest_paid
            bal_outstanding = client.loan_balance - amount_paid
            pay = Payments(amount_paid=amount_paid, client=client.id, payment_date=form.date.data, principal_paid=principal_paid, interest_paid=interest_paid, bal_outstanding=bal_outstanding)
            db.session.add(pay)
            client.loan_balance = bal_outstanding
            db.session.commit()
            flash('Paymment has been added')
            return redirect(url_for('client_blueprint.client', id=client.id))
    return render_template('add_payments.html', form=form)
