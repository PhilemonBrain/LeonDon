


def accs_under_officer():
    staff = Staff.query.filter_by(email=current_user.email).first_or_404()
    client = Client.query.filter_by(account_officer=staff.id).order_by(Client.loan_date.desc())
    return client


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request', sender='noreply4PhilProject@gmail.com', recipients=[user.email])
    msg.body = f''' TO reset your password, visit the following link:
{url_for('password_reset', token=token, _external=True)}


If you did not make this request then simply igonre this email and no changes will be made
'''
    mail.send(msg)

