from flask import Blueprint, url_for, request, render_template, redirect, flash
from ldon import bcrypt
from flask_login import login_user, logout_user, login_required, current_user
from ..staff.utils import accs_under_officer
from ldon.models import Payments, Staff
from .forms import LoginForm


main_blueprint = Blueprint('main', __name__)


@main_blueprint.route('/')
@main_blueprint.route('/home')
@login_required
def home():
    page = request.args.get('page', 1, type=int)
    pays = Payments.query.order_by(Payments.payment_date.desc()).paginate(per_page=5, page=page)
    # clients = Client.query.get_or_404(pay.client)
    # updates = Updates.query.all()
    return render_template('home.html', pays=pays, client=accs_under_officer())


@main_blueprint.route('/about')
def about():
    return "About Page"


@main_blueprint.route('/login', methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        staff = Staff.query.filter_by(email=form.email.data).first()
        if staff and bcrypt.check_password_hash(staff.password, form.password.data):
            login_user(staff, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
            flash('Login Successful.', 'success')
        else:
            flash('Login unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@main_blueprint.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))
