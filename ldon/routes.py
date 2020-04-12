import secrets
import os
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from ldon import app, bcrypt, db, mail
from ldon.forms import LoginForm, RegistrationForm, UpdateAccountForm, RequestResetForm, ResetPasswordForm, PaymentForm
from ldon.models import Staff, Client, Payments
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message



# @app.route('/register')
# def register():
#     from = RegistrationForm()
#     if form.validate_on_submit():
#         hashed_password = bcrypt.generate_password_hash(form.password.data)
#         user = Client(full_name=form.full_name.data, password=hashed_password, loan_balance=from.loan_b.data, ) #incomplete
