from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from flask_login import LoginManager
#from flask_openid import COMMON_PROVIDERS


app = Flask(__name__)
app.config['SECRET_KEY'] = "this is a super secure key"
#app.config['OPENID_PROVIDERS'] = COMMON_PROVIDERS
# remember to change to heroku's databas
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://project:project@localhost/project"
#app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://yzicurmnvkqqhp:Kpl-6hLvDaRcPCelsrxdmydSgi@ec2-23-21-219-209.compute-1.amazonaws.com:5432/de7vj5i2j9deb1"
db = SQLAlchemy(app)
lm = LoginManager()
lm.init_app(app)

from app import views
