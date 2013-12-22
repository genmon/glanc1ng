
from flask import current_app
from flask_wtf import Form
from wtforms import TextField, validators

validators = {
	'twitter_display_name': [
		validators.Required(),
		validators.Length(min=2, max=16),
		validators.Regexp(r'^@[a-zA-Z0-9_]{1,15}$', message='Twitter handles start with @ and then have only letters, numbers and underscores')
	]
}

class AddGroupMemberForm(Form):
	twitter_display_name = TextField('twitter_display_name', validators['twitter_display_name'], default='@twitter_name')

class RemoveGroupMemberForm(Form):
	pass

class DoGlanceForm(Form):
	pass