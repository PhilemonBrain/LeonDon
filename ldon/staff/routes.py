from flask import Blueprint, url_for, redirect, render_template, request, flash
from flask_login import current_user, login_required
from ldon import bcrypt
from ldon import db
from ..client.forms import UpdateAccountForm
from .forms import RequestResetForm, ResetPasswordForm
from ..client.utils import save_picture
from .utils import send_reset_email, accs_under_officer
from ldon.models import Staff, Client


staff_blueprint = Blueprint('Staff', __name__)


@staff_blueprint.route('/account', methods=['POST', 'GET'])
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
        return redirect(url_for('staff_blueprint.account'))
    elif request.method == 'GET':
        form.full_name.data = current_user.full_name
        form.email.data = current_user.email
    img_file = url_for('static', filename='profile_pics/' + current_user.staff_image)
    return render_template('account.html', title='Account', img_file=img_file, form=form, client=accs_under_officer())


@staff_blueprint.route('/user/<string:email>')
@login_required
def staff_clients(email):
    page = request.args.get('page', 1, type=int)
    staff = Staff.query.filter_by(email=email).first_or_404()
    clients = Client.query.filter_by(account_officer=staff.id).order_by(Client.loan_date.desc()).paginate(per_page=5, page=page)
    # updates = Updates.query.all()
    return render_template('staff_clients.html', clients=clients, staff=staff)


@staff_blueprint.route('/reset_request', methods=['POST', 'GET'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main_blueprint.home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        staff = Staff.query.filter_by(email=form.email.data).first()
        send_reset_email(staff)
        flash(f'An email hass been sent to {form.email.data}', 'info')
        return redirect(url_for('main_blueprint.login'))
    return render_template('reset_request.html', form=form, title='Reset Password')


@staff_blueprint.route('/reset_request/<token>', methods=['POST', 'GET'])
def password_reset(token):
    if current_user.is_authenticated:
        return redirect(url_for('main_blueprint.home'))
    staff = Staff.verify_reset_token(token)
    if staff is None:
        flash('Invalid Or expired token', 'warning')
        return redirect(url_for('staff_blueprint.password_reset'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        password = bcrypt.generate_password_hash(form.password.data)
        staff.password = password
        db.session.commit()
        flash('Password has been updated', 'success')
        return redirect(url_for('main_blueprint.login'))
    return render_template('password_reset.html', form=form, title='Reset Password')
