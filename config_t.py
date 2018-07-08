import os

BLOG_NAME = 'VeekXT'
GITHUB_LINK = 'https://github.com/veekxt/my_site'

BOOTSTRAP_SERVE_LOCAL = True
SECRET_KEY = os.environ.get("VSECRET_KEY")

# database
DATABASE = os.environ.get("VDATABASE")
SQLALCHEMY_DATABASE_URI = DATABASE
SQLALCHEMY_COMMIT_ON_TEARDOWN = True
SQLALCHEMY_TRACK_MODIFICATIONS = False

# admin
#ADMIN_NAME = 'veekxt'
#ADMIN_PASSWORD = '123456'

#email
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = "587"
MAIL_USE_TLS = True
#MAIL_USE_SSL = True
MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")

VEEKXT_MAIL_SENDER = "VeekXT <veekxt@gmail.com>"


