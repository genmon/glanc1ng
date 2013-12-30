# once upon a time I did this in my project home directory
# heroku config:set HEROKU=1
# and now configuration knows when I'm using HEROKU or not
# I've also done heroku config:set x=1
# for TWITTER_CONSUMER_KEY and TWITTER_CONSUMER_SECRET

import os
basedir = os.path.abspath(os.path.dirname(__file__))

if os.environ.get('DATABASE_URL') is None:
	#SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
	SQLALCHEMY_DATABASE_URI = 'postgres://localhost/glanc1ng_db'
else:
	SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']

SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

CSRF_ENABLED = True
SECRET_KEY = 'you-will-never-guess'

if os.environ.get('HEROKU'):
	GOOGLE_ANALYTICS = True
	if os.environ.get('DEBUG') and os.environ['DEBUG'] == 1:
		DEBUG = True
	else:
		DEBUG = False
else:
	GOOGLE_ANALYTICS = False
	DEBUG = True

# Social stuff
SOCIAL_TWITTER = {
	'consumer_key': os.environ['TWITTER_CONSUMER_KEY'],
	'consumer_secret': os.environ['TWITTER_CONSUMER_SECRET']
}
SOCIAL_APP_URL = "http://www.glanc1ng.com/"
SECURITY_LOGIN_URL = "/"
SECURITY_TRACKABLE = True
SECURITY_PASSWORD_HASH = 'bcrypt'