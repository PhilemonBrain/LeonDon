import os


class Config:
    SECRET_KEY = '820867a4cdfdd878b6a657fb5e0337b0'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
    FLASK_ADMIN_SWATCH = 'cerulean'
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('EMAIL_USER')
    MAIL_PASSWORD = os.environ.get('EMAIL_PASS')