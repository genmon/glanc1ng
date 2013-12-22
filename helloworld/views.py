from flask import render_template, request, redirect, url_for, abort, session, flash
from flask.ext.security import login_required, current_user, login_user
from flask.ext.social.views import connect_handler
from flask.ext.social.utils import get_provider_or_404

from forms import AddGroupMemberForm, RemoveGroupMemberForm
from models import WhoYouLookinAt

from . import app, db

@app.route("/")
@app.route("/index")
def index():
	if current_user.is_authenticated() is False:
		return render_template("index_signed_out.html")
		
	return render_template("index.html", current_user=current_user)

@app.route("/test")
@login_required
def test():
	return render_template("test.html", current_user=current_user)

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

@app.route("/twitter_friends")
@login_required
def twitter_friends():
	twitter_api = get_provider_or_404('twitter').get_api()
	twitter_conn = app.social.twitter.get_connection()
	print twitter_conn.provider_user_id
	
	friends = twitter_api.GetFriendIDs(user_id=twitter_conn.provider_user_id)
	
	return render_template("twitter_friends.html", twitter_friends=friends)

@app.route("/group", methods=['GET', 'POST'])
@login_required
def group():
	add_form = AddGroupMemberForm()
	remove_form = RemoveGroupMemberForm()
	if request.method == 'POST' and add_form.validate():
		test = WhoYouLookinAt.query.filter_by(user_id=current_user.id, looking_at_twitter_display_name=add_form.twitter_display_name.data).first()
		twitter_conn = app.social.twitter.get_connection()
		if test is not None:
			flash('That member is already in your group!')
		elif add_form.twitter_display_name.data.lower() == twitter_conn.display_name.lower():
			flash('You can\'t add yourself!')
		else:
			new_group_member = WhoYouLookinAt(user_id=current_user.id, looking_at_twitter_display_name=add_form.twitter_display_name.data)
			db.session.add(new_group_member)
			db.session.commit()
			flash('You added a member to your group!')
	return render_template("group.html", lookin_at=current_user.who_they_lookin_at, add_form=add_form, remove_form=remove_form)

@app.route("/group/<member>/remove", methods=['POST'])
@login_required
def group_member_remove(member=None):
	if not member:
		abort(404)

	lookin_at = WhoYouLookinAt.query.filter_by(user_id=current_user.id, looking_at_twitter_display_name="@"+member).first_or_404()

	form = RemoveGroupMemberForm()
	
	if request.method == 'POST' and form.validate():
		db.session.delete(lookin_at)
		db.session.commit()
		flash('Member removed!')
	else:
		flash('Something went wrong!')
		
	return redirect(url_for('group'))

