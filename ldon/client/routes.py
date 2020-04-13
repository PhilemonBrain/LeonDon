from flask import render_template, url_for, flash, redirect, request, abort, Blueprint
from ldon import bcrypt, db
from .forms import RegistrationForm, UpdateAccountForm
from ldon.models import Client, Payments
from flask_login import current_user, login_required
from .utils import save_picture
from ..staff.utils import accs_under_officer


client_blueprint = Blueprint('Client', __name__)


@client_blueprint.route('/accounts')
@login_required
def accounts():
    page = request.args.get('page', 1, type=int)
    clients = Client.query.order_by(Client.loan_date.desc()).paginate(per_page=5, page=page)
    # updates = Updates.query.all()
    return render_template('accounts.html', clients=clients, client=accs_under_officer())


@client_blueprint.route('/client/new', methods=['POST', 'GET'])
@login_required
def new_client():
    form = RegistrationForm()
    if form.validate_on_submit():
        password = bcrypt.generate_password_hash(form.password.data)
        if form.picture.data:
            client = Client(full_name=form.full_name.data, email=form.email.data, client_image=save_picture(form.picture.data), password=password, loan_amount=form.amount.data, loan_balance=form.amount.data, account_officer=current_user.id)
        else:
            client = Client(full_name=form.full_name.data, email=form.email.data, password=password, loan_amount=form.amount.data, account_officer=current_user.id)
        db.session.add(client)
        db.session.commit()
        flash('Account Created Successfully', 'success')
        return redirect(url_for('main_blueprint.home'))
    return render_template('new_client.html', title='Register Client', legend='New Client', form=form)


@client_blueprint.route('/client/<int:id>')
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


@client_blueprint.route('/client/<int:id>/update', methods=['POST', 'GET'])
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
        return redirect(url_for('client_blueprint.client', id=clients.id))
    elif request.method == 'GET':
        form.email.data = clients.email
        form.full_name.data = clients.full_name
    return render_template('update_client.html', legend='Update Post', form=form)


@client_blueprint.route('/client/<int:id>/delete', methods=['POST'])
@login_required
def delete_client(id):
    client = Client.query.get_or_404(id)
    if client.account_officer != current_user:
        abort(403)
    db.session.delete(client)
    db.session.commit()
    flash('Client has been data has been deleted')
    return redirect(url_for('main_blueprint.home'))
