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
	
	__tablename__ = "whoyoulookinat"
	__table_args__ = (db.UniqueConstraint('user_id', 'looking_at_twitter_display_name'),)
	
	user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
	looking_at_twitter_display_name = db.Column(db.String(255), primary_key=True)


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
	