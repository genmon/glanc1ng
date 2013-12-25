from flask import render_template, request, redirect, url_for, abort, session, flash
from flask.ext.security import login_required, current_user, login_user
from flask.ext.social.views import connect_handler
from flask.ext.social.utils import get_provider_or_404

from forms import AddGroupMemberForm, RemoveGroupMemberForm, DoGlanceForm
from models import WhoYouLookinAt, Connection, NoticedGlance

from . import app, db
from helpers import time_ago_human_readable

import datetime

@app.route("/index")
@app.route("/")
def index():
	if current_user.is_authenticated() is False:
		return render_template("index_signed_out.html")
	
	glance_form = DoGlanceForm()
	
	return render_template("index.html", glance_form=glance_form)

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

#@app.route("/twitter_friends")
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
			flash('That member is already in your group!', 'error')
		elif add_form.twitter_display_name.data.lower() == twitter_conn.display_name.lower():
			flash('You can\'t add yourself!', 'error')
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

@app.route("/do_glance", methods=['POST'])
@login_required
def do_glance():
	glance_form = DoGlanceForm()
	twitter_conn = app.social.twitter.get_connection()
	
	will_receive = []
	wont_receive = []
	if request.method == 'POST' and glance_form.validate():
		# record noticed glances here
		for receiver in current_user.who_they_lookin_at:
			# is the receiver (a) signed up and (b) looking at the sender?
			notice = False
			receiver_conn = Connection().query.filter_by(
				display_name=receiver.looking_at_twitter_display_name).first()
			if receiver_conn is not None:
				will_notice = [x.looking_at_twitter_display_name for x in receiver_conn.user.who_they_lookin_at]
				if twitter_conn.display_name in will_notice:
					notice = True
			
			if notice is True:
				will_receive.append(receiver.looking_at_twitter_display_name)
				
				# @todo record the glance
				#receiver_user_id
				#sender_twitter_display_name
				glance = NoticedGlance().query.filter_by(
					receiver_user_id = receiver_conn.user_id,
					sender_twitter_display_name = twitter_conn.display_name
					).first()
				if glance is not None:
					glance.when = datetime.datetime.utcnow()
					db.session.merge(glance)
					db.session.commit()
				else:
					glance = NoticedGlance(
						receiver_user_id = receiver_conn.user_id,
						sender_twitter_display_name = twitter_conn.display_name,
						when = datetime.datetime.utcnow())
					db.session.add(glance)
					db.session.commit()
			else:
				wont_receive.append(receiver.looking_at_twitter_display_name)

	session['glance_done'] = True
	return redirect(url_for("list_glances"))

	return render_template("do_glance_DEBUG.html", will_receive=will_receive, wont_receive=wont_receive)

@app.route("/list_glances")
@login_required
def list_glances():
	""" Displays a list of [(from, when),]
	where _when_ is None if a glance has have been received.
	"""
	
	if session.pop('glance_done', None) is not True:
		flash("Glance first to see your group!", "error")
		return redirect(url_for("index"))
	
	received_glances = []
	lookin_at = [x.looking_at_twitter_display_name for x in current_user.who_they_lookin_at]
	noticed = dict( [(n.sender_twitter_display_name, n.when) for n in current_user.noticed_glances] )
	for sender in lookin_at:
		received_glances.append( (sender, time_ago_human_readable(noticed.get(sender)) % sender) )

	twitter_conn = app.social.twitter.get_connection()
	current_user_twitter_display_name = twitter_conn.display_name

	glance_form = DoGlanceForm()
	
	return render_template("list_glances.html", received_glances=received_glances, glance_form=glance_form, current_user_twitter_display_name=current_user_twitter_display_name)

@app.route("/about")
def about():
	return render_template("about.html")
	