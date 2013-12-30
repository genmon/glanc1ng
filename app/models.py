from flask.ext.security import UserMixin, RoleMixin

from . import db

roles_users = db.Table('roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('users.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('roles.id')))

class Role(db.Model, RoleMixin):

	__tablename__ = "roles"

	id = db.Column(db.Integer(), primary_key=True)
	name = db.Column(db.String(80), unique=True)
	description = db.Column(db.String(255))

class User(db.Model, UserMixin):

	__tablename__ = "users"

	id = db.Column(db.Integer, primary_key=True)
	email = db.Column(db.String(255), unique=True)
	password = db.Column(db.String(120))
	active = db.Column(db.Boolean())
	last_login_at = db.Column(db.DateTime())
	current_login_at = db.Column(db.DateTime())
	last_login_ip = db.Column(db.String(100))
	current_login_ip = db.Column(db.String(100))
	login_count = db.Column(db.Integer)
	roles = db.relationship('Role', secondary=roles_users,
		backref=db.backref('users', lazy='dynamic'))
	connections = db.relationship('Connection',
		backref=db.backref('user', lazy='joined'), cascade="all")
		
	# The 'cascade="all"' in the following relationships means that
	# the rows using the user_id are DELETED if this user is
	# deleted! The alternative is to leave the cascade out, and then
	# a user deletion results in the user_id in those tables being
	# replaced with a null -- which often results in an error.
	# So user deletion results in data being deleted!
	who_they_lookin_at = db.relationship('WhoYouLookinAt', backref=db.backref('users', lazy='joined'), cascade="all")
	noticed_glances = db.relationship('NoticedGlance', backref=db.backref('users', lazy='joined'), cascade="all")
	last_sent_glance = db.relationship('LastSentGlance', backref=db.backref('users'), cascade="all", uselist=False)
	unnoticed_glances = db.relationship('UnnoticedGlance', backref=db.backref('users', lazy='joined'), cascade="all")
	last_unnoticed_glance = db.relationship('LastUnnoticedGlance', backref=db.backref('users'), cascade="all", uselist=False)

	def __repr__(self):
		return '<User %r>' % (self.email)

class Connection(db.Model):

	__tablename__ = "connections"
	
	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
	provider_id = db.Column(db.String(255))
	provider_user_id = db.Column(db.String(255))
	access_token = db.Column(db.String(255))
	secret = db.Column(db.String(255))
	display_name = db.Column(db.String(255))
	full_name = db.Column(db.String(255))
	profile_url = db.Column(db.String(512))
	image_url = db.Column(db.String(512))
	rank = db.Column(db.Integer)

class WhoYouLookinAt(db.Model):
	""" When a user makes their group, what they are saying is:
	
	1. When I glance, SEND the glance at these people
	2. When any of these people glance, make sure I notice it
	
	There is no requirement that any of the people in the group
	are signed up on the system, so we don't have their user IDs.
	"""
	
	__tablename__ = "whoyoulookinat"
	__table_args__ = (db.UniqueConstraint('user_id', 'looking_at_twitter_display_name'),)
	
	user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
	looking_at_twitter_display_name = db.Column(db.String(255), primary_key=True)

class NoticedGlance(db.Model):
	""" When a user makes a glance, they're definitely signed up. And
	since SENT glances are only noticed and recorded if the RECEIVER
	happens to be looking in that direction, we know that the RECEIVER
	is signed up too.
	
	This table is used by a user to show how many glances they have
	received. But by the time the receiver logs in, the sender might
	not be on the system any longer.
	
	So for noticed glances:
	
	- for every RECEIVER user_id
	- we store a list of SENDER twitter display names
	
	(and a count of how many times this particular glance has been
	noticed.)
	"""

	__tablename__ = "noticed_glance"
	__table_args__ = (db.UniqueConstraint('receiver_user_id', 'sender_twitter_display_name'),)
	
	receiver_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
	sender_twitter_display_name = db.Column(db.String(255), primary_key=True)
	when = db.Column(db.DateTime())
	count = db.Column(db.Integer, default=1)

class UnnoticedGlance(db.Model):
	""" If a glance is made and fails to make it as NoticedGlance
	because the received isn't looking back at the sender, it gets
	captured here anonymously. Unnoticed glances are kept only for 1 day,
	and I don't want to have a background job flushing the table so we
	have weird incrementing days and looping hours instead
	"""
	
	__tablename__ = "unnoticed_glance"
	__table_args__ = (db.UniqueConstraint('receiver_user_id', 'hour'),)
	
	receiver_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
	hour = db.Column(db.Integer, primary_key=True)
	ordinal_day = db.Column(db.Integer)
	count = db.Column(db.Integer)

class LastUnnoticedGlance(db.Model):
	""" Stores the most recent unnoticed glance """
	
	__tablename__ = "last_unnoticed_glance"
	
	receiver_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
	when = db.Column(db.DateTime())

class LastSentGlance(db.Model):
	""" Records the most recent glance sent by any given user.
	
	@todo delete when refactoring! """
	
	__tablename__ = "last_sent_glance"
	
	sender_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
	when = db.Column(db.DateTime())
	count = db.Column(db.Integer, default=1)


class ReceivedUnnoticedGlance(db.Model):
	""" If a glance is made and fails to make it as RecievedNoticedGlance
	because the received isn't looking back at the sender, it gets
	captured here anonymously. Unnoticed glances are kept only for 1 day,
	and I don't want to have a background job flushing the table so we
	have weird incrementing days and looping hours instead
	"""

	__tablename__ = "received_unnoticed_glance"
	__table_args__ = (db.UniqueConstraint('receiver_twitter_id', 'hour'),)

	receiver_twitter_id = db.Column(db.Integer, primary_key=True)
	hour = db.Column(db.Integer, primary_key=True)
	ordinal_day = db.Column(db.Integer)
	count = db.Column(db.Integer)

class MostRecentReceivedUnnoticedGlance(db.Model):
	""" Stores the most recent unnoticed glance """

	__tablename__ = "most_recent_received_unnoticed_glance"

	receiver_twitter_id = db.Column(db.Integer, primary_key=True)
	when = db.Column(db.DateTime())

class ReceivedNoticedGlance(db.Model):
	""" A count of all glances received by a user (identified
	by Twitter ID). To receive and NOTICE a glance, the receiver
	must be looking at the sender at the time the glance was sent.
	"""
	
	__tablename__ = "received_noticed_glance"
	__table_args__ = (db.UniqueConstraint('receiver_twitter_id', 'sender_twitter_id'),)

	receiver_twitter_id = db.Column(db.Integer, primary_key=True)
	sender_twitter_id = db.Column(db.Integer, primary_key=True)
	most_recent = db.Column(db.DateTime())
	count = db.Column(db.Integer, default=1)

class SentGlance(db.Model):
	""" Records sent glances sent by a given user """
	
	__tablename__ = "sent_glance"
	
	twitter_id = db.Column(db.Integer, primary_key=True)
	most_recent = db.Column(db.DateTime(), nullable=False)
	count = db.Column(db.Integer, nullable=False)

class TwitterFriendsCacheLastUpdated(db.Model):
	""" Records when the cache of Twitter friends was last updated
	for each user. """
	
	__tablename__ = "twitter_friends_cache_last_updated"
	
	twitter_id = db.Column(db.Integer, primary_key=True)
	when = db.Column(db.DateTime(), nullable=False)

class TwitterFriendsCache(db.Model):
	""" Caches the list of Twitter friends for each user. """
	
	__tablename__ = "twitter_friends_cache"
	__table_args__ = (db.UniqueConstraint('twitter_id', 'friend_twitter_id'),)
	
	twitter_id = db.Column(db.Integer, primary_key=True)
	friend_twitter_id = db.Column(db.Integer, primary_key=True)
