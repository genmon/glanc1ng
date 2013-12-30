from flask import render_template, request, redirect, url_for, abort, session, flash
from flask.ext.security import login_required, current_user, login_user
from flask.ext.social.views import connect_handler
from flask.ext.social.utils import get_provider_or_404
from sqlalchemy.sql import func

from forms import AddGroupMemberForm, RemoveGroupMemberForm, DoGlanceForm
from models import User, WhoYouLookinAt, Connection, SentGlance, ReceivedNoticedGlance

from . import app, db
import helpers

from datetime import datetime

@app.route("/index")
@app.route("/")
def index():
	if current_user.is_authenticated() is False:
		return render_template("index_signed_out.html")

	# list of tuples (twitter_name, twitter_id) where twitter_id is None
	# if that user hasn't registered
	group = helpers.get_group(user=current_user)
	senders = helpers.get_received_noticed_glances(user=current_user)
	senders_dict = dict( [(r.sender_twitter_id, r) for r in senders] )

	# we want an entry in received_glances for every person in group
	received_glances = []
	for sender_name, sender_id in group:
		if sender_id is None:
			# this member of the group is not registered
			received_glances.append((sender_name, None))
		elif senders_dict.has_key(sender_id):
			# this member of the group is registered, and
			# has also sent a glance at receiver
			received_glances.append(
					(sender_name, senders_dict[sender_id].most_recent) )
		else:
			# this member of the group is registered, but
			# has never sent a glance at receiver
			received_glances_human.append((sender_name, None))
	
	last_sent_glance = helpers.get_most_recent_sent_glance(user=current_user)

	group_energy = helpers.calculate_group_energy(last_sent_glance=last_sent_glance, received_glances=received_glances)

	received_glances_human = [(s, helpers.time_ago_human_readable(w) % s) for (s, w) in received_glances]

	# get count of unnoticed glances
	unnoticed_count = helpers.get_received_unnoticed_glances_count(
						user=current_user,
						db_session=db.session)

	twitter_conn = app.social.twitter.get_connection()
	current_user_twitter_display_name = twitter_conn.display_name

	glance_form = DoGlanceForm()
	
	group_tweet_text = "hey you :) "
	group_tweet_text += " ".join([s for (s, w) in received_glances])	
	
	# will be True if do_glance was called
	show_group = session.pop('glance_done', False)
	
	return render_template("index.html",
		show_group=show_group,
		received_glances=received_glances_human,
		glance_form=glance_form,
		current_user_twitter_display_name=current_user_twitter_display_name,
		group_energy=group_energy,
		group_size=len(current_user.who_they_lookin_at),
		group_tweet_text=group_tweet_text,
		unnoticed_count=unnoticed_count)

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

# will replace do_glance eventually
# @todo remove GET and remove the "if False" below
@app.route("/send_glance", methods=['GET', 'POST'])
@login_required
def send_glance():
	""" Sends a glance to all Twitter friends of the logged-in user.
	
	Launch functionality:
	
	- all glance-related tables now use twitter_id (an integer)
	- updates the local cache of twitter friendships if required
	- saves that a glance was sent by this user
	- for all twitter friends of this user:
		- logs an unnoticed glance for that receiver (appears to the
		  sender anonymously for 24 hour). all do this!
		- if the friend is a registered user and looking back,
		  logs a noticed glance for that receiver too (appears to the
		  sender named and forever)
	- commits the session
	
	@todo functionality:
	
	- cache mutual friendships of all this user's friends
		- (requires friendships/lookup.json added to python-twitter)
	- for all twitter friends of this user:
		- if the friend is a mutual friend and not looking back,
		  logs a transitory glance (appears to the sender named
		  for an hour, then anonymously for 24 hours). This is in
		  addition to the unnoticed glance	
	"""
	
	# check whether we're really sending the glance
	glance_form = DoGlanceForm()
	if False and not (request.method == 'POST' and glance_form.validate()):
		flash("Glance not successful", "error")
		return redirect(url_for('index'))
	
	# everything following works from the sender's Twitter ID
	sender_twitter_id = helpers.get_twitter_id(user=current_user)
	
	# update the cache of the sender's twitter friends
	# @todo this needs to also update mutual friendships
	commit_required = helpers.update_twitter_friends_cache(
		twitter_id=sender_twitter_id,
		twitter_api=get_provider_or_404('twitter').get_api(),
		db_session=db.session)
	if commit_required:
		db.session.commit()

	# log the sent glance. note no commit... the next time we commit
	# is at the end of the function
	helpers.log_sent_glance(
		sender_twitter_id=sender_twitter_id,
		db_session=db.session) # db not yet committed!

	# loop over all twitter friends of the sender... these are
	# all receivers
	receivers = helpers.get_twitter_friends(twitter_id=sender_twitter_id)
	
	# loads the twitter IDs of receivers who will notice this
	will_notice_list = helpers.get_reverse_group_as_twitter_ids(
									user=current_user)
	def glance_is_noticed(r):
		if r in will_notice_list:
			return True
		else:
			return False

	# every receiver gets an unnoticed glance
	helpers.log_unnoticed_glances(
		receivers=receivers,
		db_session=db.session)
	# and we need to delete old unnoticed glances too
	helpers.sweep_unnoticed_glances(
		receivers=receivers,
		db_session=db.session)
	

	for receiver_twitter_id in receivers:

		# additionally the receiver might get a noticed or a transitory
		# glance
		if glance_is_noticed(receiver_twitter_id):
			# if the receiver is a registered user and the sender is in the
			# receiver's group, this glance will be noticed
			helpers.log_noticed_glance(
				sender_twitter_id=sender_twitter_id,
				receiver_twitter_id=receiver_twitter_id,
				db_session=db.session)
		elif helpers.glance_is_transitory(
								sender_user=current_user,
								receiver_twitter_id=receiver_twitter_id):
			# the glance might also be transitory, in which
			# case it has a chance of being seen by the user
			# @todo add transitory glances
			pass
	
	# commit and finish up
	db.session.commit()
	session['glance_done'] = True
	return redirect(url_for('index'))


#@app.route("/user/remove")
@login_required
def user_remove():
	""" Deletes the current user and associated Twitter connections. """
	ds = app.security.datastore
	ds.delete_user(current_user)
	ds.commit()
	flash("User deleted")
	return redirect(url_for('index'))


@app.route("/about")
def about():
	return render_template("about.html")

# login required because this hammers the database
# and UNLINKED from the main site
@app.route("/about/stats")
@login_required
def stats():
	# "None" below means we have to calculate it
	stats = {
		'registered_users': int(User.query.count()),
		'groups': int(WhoYouLookinAt.query.distinct('user_id').count()),
		'all_users': None,
		'memberships': int(WhoYouLookinAt.query.count()),
		'memberships_of_registered_users': None,
		'reciprocated_memberships': None,
		'mean_formed_group_size': None,
		'sent_glances': 0,
		'noticed_glances': 0
	}
	
	# all_users
	registered = [r.display_name for r in Connection.query.all()]
	unregistered = [r.looking_at_twitter_display_name for r in WhoYouLookinAt.query.distinct('looking_at_twitter_display_name').all()]
	stats['all_users'] = len(set(registered + unregistered))
	
	# memberships_of_registered_users
	# reciprocated_memberships
	registered_memberships = [(w.user_id, c.user_id)
		for w, c
		in WhoYouLookinAt.query.outerjoin(Connection, WhoYouLookinAt.looking_at_twitter_display_name==Connection.display_name).filter(Connection.display_name != None).add_entity(Connection).all()]
	stats['memberships_of_registered_users'] = len(registered_memberships)
	count = 0
	for pair in registered_memberships:
		if (pair[1], pair[0]) in registered_memberships:
			count += 1
	stats['reciprocated_memberships'] = count
	
	# mean_formed_group_size
	stats['mean_formed_group_size'] = "%.1f" % (float(stats['memberships'])/stats['groups'])
	
	# sent_glances
	r = db.session.query(func.sum(SentGlance.count)).filter(SentGlance.count != None).first()[0]
	if r is None:
		r = 0
	stats['sent_glances'] = int(r)

	# noticed_glances
	r = db.session.query(func.sum(ReceivedNoticedGlance.count)).filter(ReceivedNoticedGlance.count != None).first()[0]
	if r is None:
		r = 0
	stats['noticed_glances'] = int(r)
	
	return render_template("about_stats.html", **stats)

	