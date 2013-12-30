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
	who_they_lookin_at = db.relationship('WhoYouLookinAt', backref=db.backref('user', lazy='joined'), cascade="all")

	def __repr__(self):
		return '<User %r>' % (self.email)

class Connection(db.Model):

	__tablename__ = "connections"
	
	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
	provider_id = db.Column(db.String(255))
	provider_user_id = db.Column(db.String(255), index=True)
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

class ReceivedUnnoticedGlance(db.Model):
	""" When a glance is sent, it is captured here anonymously. All 
	sent glances are stored here. They might also be noticed or
	transitory. Unnoticed glances are kept only for 1 day.
	"""

	__tablename__ = "received_unnoticed_glance"

	receiver_twitter_id = db.Column(db.String(255), primary_key=True)
	when = db.Column(db.DateTime(), index=True)

class ReceivedNoticedGlance(db.Model):
	""" A count of all glances received by a user (identified
	by Twitter ID). To receive and NOTICE a glance, the receiver
	must be looking at the sender at the time the glance was sent.
	"""
	
	__tablename__ = "received_noticed_glance"
	__table_args__ = (db.UniqueConstraint('receiver_twitter_id', 'sender_twitter_id'),)

	receiver_twitter_id = db.Column(db.String(255), primary_key=True)
	sender_twitter_id = db.Column(db.String(255), primary_key=True)
	most_recent = db.Column(db.DateTime())
	count = db.Column(db.Integer, default=1)

class SentGlance(db.Model):
	""" Records sent glances sent by a given user """
	
	__tablename__ = "sent_glance"
	
	twitter_id = db.Column(db.String(255), primary_key=True)
	most_recent = db.Column(db.DateTime(), nullable=False)
	count = db.Column(db.Integer, nullable=False)

class TwitterFriendsCacheLastUpdated(db.Model):
	""" Records when the cache of Twitter friends was last updated
	for each user. """
	
	__tablename__ = "twitter_friends_cache_last_updated"
	
	twitter_id = db.Column(db.String(255), primary_key=True)
	when = db.Column(db.DateTime(), nullable=False)

class TwitterFriendsCache(db.Model):
	""" Caches the list of Twitter friends for each user. """
	
	__tablename__ = "twitter_friends_cache"
	__table_args__ = (db.UniqueConstraint('twitter_id', 'friend_twitter_id'),)
	
	twitter_id = db.Column(db.String(255), primary_key=True)
	friend_twitter_id = db.Column(db.String(255), primary_key=True)
