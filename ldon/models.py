from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from ldon import db, login_manager, app
from flask_login import UserMixin, current_user, login_user, logout_user
from flask_admin.contrib.sqla import ModelView
from flask import redirect, url_for, request, flash
from flask_admin import Admin, expose, AdminIndexView, BaseView
from ldon.main.forms import LoginForm
from ldon import bcrypt


@login_manager.user_loader
def load_user(user_id):
    staff = Staff.query.get(int(user_id))
    client = Client.query.get(int(user_id))
    if staff:
        return db.session.query(Staff).get(int(user_id))
    elif client:
        return db.session.query(Client).get(int(user_id))


class Staff(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    staff_image = db.Column(db.String(20), default='default.jpg')      # 'should i use a general name'account image for this?
    password = db.Column(db.String(60), nullable=False)
    branch = db.Column(db.String(20))
    position = db.Column(db.String(30))
    phone_number = db.Column(db.Integer, unique=True)
    clients = db.relationship('Client', backref='author', lazy=True)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except Exception:
            return None
        return Staff.query.get(user_id)

    def get_id(self):
        return self.id

    def custView(self):
        return False

    def __unicode__(self):
        return self.full_name

    def __repr__(self):
        return f"{self.full_name}"


class Client(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    client_image = db.Column(db.String(20), default='default.jpg')     # should i use a general name e.g 'account_image' for this
    password = db.Column(db.String(60), nullable=False)
    phone_number = db.Column(db.Integer, unique=True, nullable=False)
    loan_amount = db.Column(db.Integer, nullable=False)
    loan_balance = db.Column(db.Integer)
    loan_date = db.Column(db.DateTime, default=datetime.utcnow)
    payments = db.relationship('Payments', backref='payer', lazy=True)
    account_officer = db.Column(db.Integer, db.ForeignKey('staff.id'), nullable=False)

    def __repr__(self):
        return f"{self.full_name}"

    def get_id(self):
        return self.id

    def custView(self):
        return True


class Payments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount_paid = db.Column(db.Integer)
    principal_paid = db.Column(db.Integer)
    interest_paid = db.Column(db.Integer)
    bal_outstanding = db.Column(db.Integer)
    client = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    payment_receipt = db.Column(db.String(20), default='default.jpg')    # file type, png, jpg or pdf
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"Payments('{self.id}', '{self.client}', '{self.payment_date}','{self.payment_receipt}')"


class PaymentView(ModelView):

    def is_accessible(self):
        return current_user.is_authenticated

    can_delete = False
    can_view_details = True


class ClientView(ModelView):

    def is_accessible(self):
        return current_user.is_authenticated

    # column_exclude_list = ['password']
    column_exclude_list = ['payments']
    column_searchable_list = ['full_name', 'loan_amount']
    column_filters = ['loan_amount', 'loan_date']
    edit_modal = True


class StaffView(ModelView):

    create_template = 'admin/models/create_user.html'

    def is_accessible(self):
        return current_user.is_authenticated

    # @expose('/new/', methods=('GET', 'POST'))
    # def scaffold_form(self):
    #     form = super(StaffView, self).scaffold_form()
    #     # if helpers.validate_form_on_submit(form):
    #     #     flash('update made', 'success')
    #     return form

    # column_exclude_list = ['password']


class CustormerView(BaseView):

    @expose('/')
    def index(self):
        return self.render('admin/customer.html')


class MyAdminView(AdminIndexView):

    @expose('/')
    def index(self):
        if not current_user.is_authenticated:
            return redirect(url_for('.login_view'))
        return self.render('admin/index.html')

    @expose('/login/', methods=['GET', 'POST'])
    def login_view(self):
        form = LoginForm()
        if form.validate_on_submit():
            staff = Staff.query.filter_by(email=form.email.data).first()
            p = form.password.data
            client = Client.query.filter_by(email=form.email.data).first()
            p2 = form.password.data
            if staff and bcrypt.check_password_hash(staff.password, p):
                login_user(staff, remember=form.remember.data)
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('.index'))
                flash('Login Successful.', 'success')
            elif client and bcrypt.check_password_hash(client.password, p2):
                login_user(client, remember=form.remember.data)
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('.index'))
                flash('Login Successful.', 'success')
                # CustormerView.
        return self.render('admin/login.html', form=form)

    @expose('/logout/')
    def logout_view(self):
        logout_user()
        return redirect(url_for('.index'))

    # def confirm_account():
    #     client = Client.query.filter_by(email=form.email.data).first()
    #     p2 = form.password.data
    #     if client and bcrypt.check_password_hash(client.password, p2):
    #         return True
    #     return False


admin = Admin(app, name='Leon', template_mode='bootstrap3', index_view=MyAdminView())
admin.add_view(StaffView(Staff, db.session))
admin.add_view(ClientView(Client, db.session))
admin.add_view(PaymentView(Payments, db.session))
admin.add_view(CustormerView(name='Customer Profile Page', endpoint='notify', menu_icon_type='glyph', menu_icon_value='glyphicon-home'))
