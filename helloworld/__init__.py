from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

# initialization
app = Flask(__name__)
app.config.from_object('config')

db = SQLAlchemy(app)

from helloworld import views
