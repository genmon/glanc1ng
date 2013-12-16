from flask import render_template, request, redirect, url_for, abort, session, flash
from flask.ext.security import login_required, current_user, login_user
from flask.ext.social.views import connect_handler
from flask.ext.social.utils import get_provider_or_404

from . import app

@app.route("/")
@app.route("/index")
def index():
	return render_template("index.html", current_user=current_user)


@app.route('/register/<provider_id>', methods=['GET', 'POST'])
def register(provider_id=None):
	if current_user.is_authenticated():
		return redirect(request.referrer or '/')

	if provider_id:
		provider = get_provider_or_404(provider_id)
		connection_values = session.pop('failed_login_connection', None)
	else:
		provider = None
		connection_values = None

	app.logger.debug("Attemption to register with connection_values: %s" % repr(connection_values))

	if connection_values is not None:
		ds = app.security.datastore
		fake_email = connection_values['provider_user_id'] + "_dummy@example.org"
		user = ds.create_user(email=fake_email, password="whatever")

		ds.commit()
		
		connection_values['user_id'] = user.id
		connect_handler(connection_values, provider)

		login_user(user)
		ds.commit()
		flash('Account created successfully', 'info')
		return redirect(url_for('index'))

	return abort(404)
