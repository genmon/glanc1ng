from flask import Flask, session, redirect, url_for
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand

from flask.ext.security import Security, SQLAlchemyUserDatastore
from flask.ext.social import Social, SQLAlchemyConnectionDatastore, login_failed
from flask.ext.social.utils import get_connection_values_from_oauth_response

# initialization
app = Flask(__name__)
app.config.from_object('config')

db = SQLAlchemy(app)
migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)

# Late import so modules can import their dependencies properly
from . import views, models

security_ds = SQLAlchemyUserDatastore(db, models.User, models.Role)
social_ds = SQLAlchemyConnectionDatastore(db, models.Connection)

app.security = Security(app, security_ds)
app.social = Social(app, social_ds)

class SocialLoginError(Exception):
	def __init__(self, provider):
		self.provider = provider

# if this is the first time somebody has tried to sign in via Twitter,
# the @login_failed signal is trigged. See:
# https://github.com/mattupstate/flask-social-example/issues/10
@login_failed.connect_via(app)
def on_login_failed(sender, provider, oauth_response):
	app.logger.debug('Social Login Failed via %s; '
		'&oauth_response=%s' % (provider.name, oauth_response))

	# Save the oauth response in the session so we can make the connection
	# later after the user possibly registers
	session['failed_login_connection'] = \
		get_connection_values_from_oauth_response(provider, oauth_response)
	raise SocialLoginError(provider)

@app.errorhandler(SocialLoginError)
def social_login_error(error):
	return redirect(url_for('register', provider_id=error.provider.id, login_failed=1))

