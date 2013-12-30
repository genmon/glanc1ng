""" Database commit policy: Helper functions DO NOT commit the db.session,
    and must always have it passed in. """

from sqlalchemy.sql import func

from . import app
from models import TwitterFriendsCacheLastUpdated, TwitterFriendsCache, SentGlance, ReceivedNoticedGlance, Connection, ReceivedUnnoticedGlance, WhoYouLookinAt

from dateutil import relativedelta
from datetime import datetime, timedelta

from random import random

def get_twitter_id(user=None):
	""" For a user object, return the Twitter ID.
	@todo be robust against multiple social network connections """
	return user.connections[0].provider_user_id

def update_twitter_friends_cache(twitter_id=None, twitter_api=None, db_session=None):
	""" For a twitter ID, update the database table containing the
	list of Twitter friends. """
	
	now = datetime.utcnow()
	
	last_updated = TwitterFriendsCacheLastUpdated.query.filter_by(
		twitter_id = twitter_id).first()
	if last_updated is None:
		last_updated = TwitterFriendsCacheLastUpdated(
			twitter_id = twitter_id,
			when = now)
		db_session.add(last_updated)
	elif (now - last_updated.when).days > 0:
		last_updated.when = now
		db_session.merge(last_updated)
	else:
		# cache update not required
		return False

	friends = twitter_api.GetFriendIDs(user_id=twitter_id)
	
	# remove existing friends from the DB and replace it with new ones
	TwitterFriendsCache.query.filter_by(
		twitter_id = twitter_id).delete()
	for f in friends:
		t = TwitterFriendsCache(
			twitter_id = twitter_id,
			friend_twitter_id = f)
		db_session.add(t)
	
	return True # will commit


def get_twitter_friends(twitter_id=None):
	""" Returns Twitter IDs of all the friends of this user """
	friends_q = TwitterFriendsCache.query.filter_by(
						twitter_id = twitter_id).all()
	
	if friends_q is None:
		friends = []
	else:
		friends = [f.friend_twitter_id for f in friends_q]
	
	return friends

	
def log_sent_glance(sender_twitter_id=None, db_session=None):
	""" Logs that this Twitter ID sent this glance. """
	
	now = datetime.utcnow()
	
	sent_glance = SentGlance.query.filter_by(
					twitter_id = sender_twitter_id).first()
	if sent_glance is not None:
		sent_glance.most_recent = now
		sent_glance.count += 1
		db_session.merge(sent_glance)
	else:
		sent_glance = SentGlance(
						twitter_id = sender_twitter_id,
						most_recent = now,
						count = 1)
		db_session.add(sent_glance)
	
	return True


def get_group(user=None):
	""" Returns the group as (twitter_name, twitter_id),
	where the twitter_id is None if the user is not registered. """
	
	group = []
	if user.who_they_lookin_at is not None:
		for u in user.who_they_lookin_at:
			display_name = u.looking_at_twitter_display_name
			conn = Connection().query.filter_by(
				display_name=display_name).first()
			if conn is not None:
				group.append( (display_name, conn.provider_user_id) )
			else:
				group.append( (display_name, None) )
	
	return group

def get_reverse_group_as_twitter_ids(user=None):
	""" Returns a list of Twitter IDs of those users who
	will notice a received glance. """
	
	twitter_name = user.connections[0].display_name
	
	reverse_group = []
	receivers = WhoYouLookinAt.query.filter_by(
			looking_at_twitter_display_name=twitter_name).all()
	if receivers is not None:
		reverse_group = [get_twitter_id(r.user) for r in receivers]
	
	return reverse_group

def get_received_noticed_glances(user=None):
	""" Returns a list of ReceivedNoticedGlance objects """
	
	twitter_id = get_twitter_id(user=user)
	
	received = ReceivedNoticedGlance.query.filter_by(
		receiver_twitter_id=twitter_id).all()
	
	return received

def get_most_recent_sent_glance(user=None):
	""" Returns the datetime of the most recently sent glance """
	
	twitter_id = get_twitter_id(user=user)
	
	glance = SentGlance.query.filter_by(twitter_id=twitter_id).first()
	
	if glance is None:
		return None
	else:
		return glance.most_recent

def get_received_unnoticed_glances_count(user=None, db_session=None):
	""" Returns the number of received, unnoticed glances in the last
	24 hours. """

	twitter_id = get_twitter_id(user=user)

	yesterday = datetime.utcnow() - timedelta(days=1)

	r = ReceivedUnnoticedGlance.query \
		.filter(ReceivedUnnoticedGlance.receiver_twitter_id == twitter_id) \
		.filter(ReceivedUnnoticedGlance.when >= yesterday) \
		.count()

	if r is None:
		r = 0
	r = int(r)

	return r

def glance_is_noticed(sender_user=None, receiver_twitter_id=None):
	""" For a glance to be noticed by a receiver, they must be
	(a) signed up, and therefore in Connection; and
	(b) they must be listed in the sender's group
	"""

	noticed = False
	
	conn = Connection.query.filter_by(
			provider_user_id=str(receiver_twitter_id)
			).enable_eagerloads(False).first()
	if conn is not None:
		receiver_twitter_name = conn.display_name
		
		if sender_user.who_they_lookin_at is not None:
			group = [r.looking_at_twitter_display_name for r in sender_user.who_they_lookin_at]
		else:
			group = []
		
		if receiver_twitter_name in group:
			noticed = True
	
	return noticed



def glance_is_transitory(sender_user=None, receiver_twitter_id=None):
	return False



def log_noticed_glance(sender_twitter_id=None, receiver_twitter_id=None, db_session=None):
	""" Logs a received and NOTICED glance to the database, counting up. """
	
	now = datetime.utcnow()
	
	glance = ReceivedNoticedGlance.query.filter_by(
				sender_twitter_id=sender_twitter_id,
				receiver_twitter_id=receiver_twitter_id).first()
	
	if glance is not None:
		glance.most_recent = now
		glance.count += 1
		db_session.merge(glance)
	else:
		glance = ReceivedNoticedGlance(
					sender_twitter_id=sender_twitter_id,
					receiver_twitter_id=receiver_twitter_id,
					most_recent=now,
					count=1)
		db_session.add(glance)
	
	return True


def log_unnoticed_glances(receivers=[], db_session=None):
	""" When a receiver is NOT looking at a sender, the glance is
	unnoticed. This means it is logged anonymously so an aggregate
	score can be shown for 24 hours. (The glance might also be
	transitory, in which case a name will be shown, but that's
	dealt with elsewhere.) """
	
	now = datetime.utcnow()
	
	for r in receivers:
		log = ReceivedUnnoticedGlance(
				receiver_twitter_id=r,
				when=now)
		db_session.add(log)

def sweep_unnoticed_glances(receivers=[], db_session=None):
	""" Since we have no background workers, we have to make sure
	the unnoticed glances table doesn't get over full. This
	function deletes old records for 1/10 of the receivers. """

	yesterday = datetime.utcnow() - timedelta(days=1)
	
	for r in receivers:
		if random < 0.9:
			pass
		
		ReceivedUnnoticedGlance.query \
			.filter(ReceivedUnnoticedGlance.receiver_twitter_id == r) \
			.filter(ReceivedUnnoticedGlance.when < yesterday) \
			.delete()	


def calculate_group_energy(last_sent_glance=None, received_glances=[]):
	""" Calculates group_energy from 0 to 4 where points are given:
	+1 for you glancing in the last 60 minutes
	+1 for one other glancing in the last 24 hours
	+1 for one other glancing in the last 60 minutes, or >1 in the last 24
	+1 for all others glancing in the last 60 minutes
	"""
	now = datetime.utcnow()
	
	# in seconds...
	one_hour = 60 * 60
	
	energy = 0
	
	# +1 for you glancing in the last 60 minutes
	if (last_sent_glance is not None) and ((now - last_sent_glance).seconds < one_hour) and ((now - last_sent_glance).days == 0):
		energy +=1
		app.logger.debug("+1 energy - last glanced within an hour")
	
	within_hour = [True for (s, w) in received_glances
					if (w is not None) and ((now - w).seconds < one_hour) and ((now - w).days == 0)]
	within_day = [True for (s, w) in received_glances
					if (w is not None) and ((now - w).days == 0)]
	
	# +1 for one other glance in the last 24 hours
	if len(within_day) > 0:
		energy += 1
		app.logger.debug("+1 energy - one other glance in last 24 hours")
	
	# +1 for one other glancing in the last 60 minutes, or >1 in the last 24
	if (len(within_hour) > 0) or (len(within_day) > 1):
		energy += 1
		app.logger.debug("+1 energy - 1 other glance in 1 hr, or >1 in 24")

	# +1 for all others glancing in the last 60 minutes
	if len(within_hour) == len(received_glances):
		energy += 1
		app.logger.debug("+1 energy - all others glance in last 1 hr")
	
	assert energy in [0, 1, 2, 3, 4]
	return energy

def pluralise(num, singular):
	if num == 0:
		return "no %ss" % singular
	elif num == 1:
		return "1 %s" % singular
	else:
		return "%d %ss" % (num, singular)

def time_ago_human_readable(dt=None):
	now = datetime.utcnow()
	
	ago_string = None
	if dt is None:
		ago_string = "You've never noticed %s glance"
	else:
		attrs = ['years', 'months', 'days', 'hours', 'minutes']
		human_readable = lambda delta: [
		    '%d %s' % (getattr(delta, attr), getattr(delta, attr) > 1 and attr or attr[:-1]) 
		        for attr in attrs if getattr(delta, attr)
		]

		r = relativedelta.relativedelta(now, dt)
		
		if r.years > 0 or r.months > 0:
			ago_string = "You last noticed %s glance over a month ago"
		
		ago_suffix = ""
		if r.days > 0:
			if r.hours == 0:
				ago_suffix = "%s ago" % pluralise(r.days, 'day')
			else:
				ago_suffix = "%s and %s ago" % (pluralise(r.days, 'day'), pluralise(r.hours, 'hour'))
		elif r.hours > 0:
			if r.minutes == 0:
				ago_suffix = "%s ago" % pluralise(r.hours, 'hour')
			else:
				ago_suffix = "%s and %s ago" % (pluralise(r.hours, 'hour'), pluralise(r.minutes, 'minute'))
		else:
			ago_suffix = "%s ago" % pluralise(r.minutes, 'minute')
		
		ago_string = "You last noticed %s glance " + ago_suffix
	
	return ago_string
