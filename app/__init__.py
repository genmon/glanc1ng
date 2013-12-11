from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

# initialization
app = Flask(__name__)
app.config.update(
	DEBUG = True,
	#SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL'],
)

db = SQLAlchemy(app)

from app import views
