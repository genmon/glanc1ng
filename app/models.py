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
	who_they_lookin_at = db.relationship('WhoYouLookinAt', backref=db.backref('users', lazy='joined'))
	noticed_glances = db.relationship('NoticedGlances', backref=db.backref('users', lazy='joined'))

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

class NoticedGlances(db.Model):
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
	"""

	__tablename__ = "noticed_glances"
	__table_args__ = (db.UniqueConstraint('receiver_user_id', 'sender_twitter_display_name'),)
	
	receiver_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
	sender_twitter_display_name = db.Column(db.String(255), primary_key=True)
	when = db.Column(db.DateTime())

"""
class Glance(db.Model):
	
	__tablename__ = "glances"
	
	# A user glances in the directions of several other users
	# In the interface we call these friends.
	
	# When a user glances at another user, that glance is only
	# recorded if the user is looking back at them
	
	sending_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
	receiving_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
	last_glance_made_at = db.Column(db.DateTime())
	last_glance_noticed_at = db.Column(db.DateTime())
	
	sending_user = db.relationship("User", foreign_keys=[sending_user_id], backref="sends_glances_to")
	receiving_user = db.relationship("User", foreign_keys=[receiving_user_id], backref="receives_glances_from")
"""
	