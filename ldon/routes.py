import secrets
import os
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from ldon import app, bcrypt, db, mail
from ldon.forms import LoginForm, RegistrationForm, UpdateAccountForm, RequestResetForm, ResetPasswordForm, PaymentForm
from ldon.models import Staff, Client, Payments
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message

posts = [
    {
        'author': 'phil brain',
        'title': 'living in bondage',
        'content': 'first blog post',
        'date_posted': 'April 21 2018'
    },
    {
        'author': 'john lison',
        'title': 'triple threat',
        'content': 'second blog post',
        'date_posted': 'June 21 2018'
    }
]


@app.route('/accounts')
@login_required
def accounts():
    page = request.args.get('page', 1, type=int)
    clients = Client.query.order_by(Client.loan_date.desc()).paginate(per_page=5, page=page)
    # updates = Updates.query.all()
    return render_template('accounts.html', clients=clients, client=accs_under_officer())


@app.route('/')
@app.route('/home')
@login_required
def home():
    page = request.args.get('page', 1, type=int)
    pays = Payments.query.order_by(Payments.payment_date.desc()).paginate(per_page=5, page=page)
    # clients = Client.query.get_or_404(pay.client)
    # updates = Updates.query.all()
    return render_template('home.html', pays=pays, client=accs_under_officer())


@app.route('/about')
def about():
    return "About Page"


@app.route('/login', methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        # hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        staff = Staff.query.filter_by(email=form.email.data).first()
        # client = Client.query.filter_by(email=form.email.data).first()
        if staff and bcrypt.check_password_hash(staff.password, form.password.data):
            login_user(staff, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
            flash('Login Successful.', 'success')
        else:
            flash('Login unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


def accs_under_officer():
    staff = Staff.query.filter_by(email=current_user.email).first_or_404()
    client = Client.query.filter_by(account_officer=staff.id).order_by(Client.loan_date.desc())
    return client


def save_picture(form_picture):
    token_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = token_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics/' + picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route('/account', methods=['POST', 'GET'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.staff_image = picture_file
        current_user.full_name = form.full_name.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your Profile has been Updated', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.full_name.data = current_user.full_name
        form.email.data = current_user.email
    img_file = url_for('static', filename='profile_pics/' + current_user.staff_image)
    return render_template('account.html', title='Account', img_file=img_file, form=form, client=accs_under_officer())


@app.route('/client/new', methods=['POST', 'GET'])
@login_required
def new_client():
    form = RegistrationForm()
    if form.validate_on_submit():
        password = bcrypt.generate_password_hash(form.password.data)
        if form.picture.data:
            client = Client(full_name=form.full_name.data, email=form.email.data, client_image=save_picture(form.picture.data), password=password, loan_amount=form.amount.data, loan_balance=form.amount.data, account_officer=current_user.id)
            #code for db addition to a general updates table
        else:
            client = Client(full_name=form.full_name.data, email=form.email.data, password=password, loan_amount=form.amount.data, account_officer=current_user.id)
        db.session.add(client)
        db.session.commit()
        flash('Account Created Successfully', 'success')
        return redirect(url_for('home'))
    return render_template('new_client.html', title='Register Client', legend='New Client', form=form)


@app.route('/client/<int:id>')
# @login_required
def client(id):
    form = RegistrationForm()
    clients = Client.query.get_or_404(id)
    payments = Payments.query.filter_by(client=clients.id).order_by(Payments.payment_date.desc())
    img_file = url_for('static', filename='profile_pics/' + clients.client_image)
    form.amount.data = clients.loan_amount
    form.email.data = clients.email
    form.full_name.data = clients.full_name
    form.date.data = clients.loan_date
    return render_template('view_client.html', title=clients.full_name, clients=clients, img_file=img_file, form=form, payments=payments)


@app.route('/client/<int:id>/update', methods=['POST', 'GET'])
@login_required
def update(id):
    clients = Client.query.get_or_404(id)
    if clients.account_officer != current_user.id:
        abort(403)
    form = UpdateAccountForm()
    if form.validate_on_submit():
        clients.email = form.email.data
        clients.full_name = form.full_name.data
        if form.picture.data:
            clients.client_image = save_picture(form.picture.data)
        db.session.commit()
        flash('Clients details has been succesfully updated', 'Success')
        return redirect(url_for('client', id=clients.id))
    elif request.method == 'GET':
        form.email.data = clients.email
        form.full_name.data = clients.full_name
    return render_template('update_client.html', legend='Update Post', form=form)


@app.route('/client/<int:id>/delete', methods=['POST'])
@login_required
def delete_client(id):
    client = Client.query.get_or_404(id)
    if client.account_officer != current_user:
        abort(403)
    db.session.delete(client)
    db.session.commit()
    flash('Client has been data has been deleted')
    return redirect(url_for('home'))


@app.route('/client/<int:id>/add_payment', methods=['POST', 'GET'])
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
            return redirect(url_for('client', id=client.id))
    return render_template('add_payments.html', form=form)


@app.route('/user/<string:email>')
@login_required
def staff_clients(email):
    page = request.args.get('page', 1, type=int)
    staff = Staff.query.filter_by(email=email).first_or_404()
    clients = Client.query.filter_by(account_officer=staff.id).order_by(Client.loan_date.desc()).paginate(per_page=5, page=page)
    # updates = Updates.query.all()
    return render_template('staff_clients.html', clients=clients, staff=staff)


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request', sender='noreply4PhilProject@gmail.com', recipients=[user.email])
    msg.body = f''' TO reset your password, visit the following link:
{url_for('password_reset', token=token, _external=True)}


If you did not make this request then simply igonre this email and no changes will be made
'''
    mail.send(msg)


@app.route('/reset_request', methods=['POST', 'GET'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        staff = Staff.query.filter_by(email=form.email.data).first()
        send_reset_email(staff)
        flash(f'An email hass been sent to {form.email.data}', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', form=form, title='Reset Password')


@app.route('/reset_request/<token>', methods=['POST', 'GET'])
def password_reset(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    staff = Staff.verify_reset_token(token)
    if staff is None:
        flash('Invalid Or expired token', 'warning')
        return redirect(url_for('password_reset'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        password = bcrypt.generate_password_hash(form.password.data)
        staff.password = password
        db.session.commit()
        flash('Password has been updated', 'success')
        return redirect(url_for('login'))
    return render_template('password_reset.html', form=form, title='Reset Password')


# @app.route('/register')
# def register():
#     from = RegistrationForm()
#     if form.validate_on_submit():
#         hashed_password = bcrypt.generate_password_hash(form.password.data)
#         user = Client(full_name=form.full_name.data, password=hashed_password, loan_balance=from.loan_b.data, ) #incomplete
