# modifying python-twitter according to
# https://code.google.com/r/lizxrice-python-twitter/
# to add ShowFriendships

# Two new classes: RelationshipUser, Relationship
# One new method to add to the Api class: ShowFriendships

import simplejson

class RelationshipUser(object):
	''' A class representing one of the users in a relationship
	'''

	def __init__(self,
				 id=None,
				 screen_name=None,
				 following=None,
				 followed_by=None,
				 notifications_enabled=None,
 				 can_dm=None,
				 want_retweets=None,
				 marked_spam=None,
				 all_replies=None,
				 blocking=None
				 ):
		self.id = id
		self.screen_name = screen_name
		self.following = following
		self.followed_by = followed_by
		self.notifications_enabled = notifications_enabled
		self.can_dm = can_dm
		self.want_retweets = want_retweets
		self.marked_spam = marked_spam
		self.all_replies = all_replies
		self.blocking = blocking

	@staticmethod
	def NewFromJsonDict(data):
		'''Create a new instance based on a JSON dict.

		Args:
			data:
				A JSON dict, as converted from the JSON in the twitter API

		Returns:
			A twitter.RelationshipUser instance
		'''
		return RelationshipUser(id = data.get('id', None),
								screen_name = data.get('screen_name', None),
								following = data.get('following', None),
								followed_by = data.get('followed_by', None),
								notifications_enabled = data.get('notifications_enabled', None),
								can_dm = data.get('can_dm', None),
								want_retweets = data.get('want_retweets', None),
								marked_spam = data.get('marked_spam', None),
								all_replies = data.get('all_replies', None),
								blocking = data.get('blocking', None))

	def __str__(self):
		'''A string representation of this twitter.RelationshipUser instance.

		The return value is the same as the JSON string representation.

		Returns:
			A string representation of this twitter.RelationshipUser instance.
		'''
		return self.AsJsonString()

	def AsJsonString(self):
		'''A JSON string representation of this twitter.RelationshipUser instance.

		Returns:
			A JSON string representation of this twitter.RelationshipUser instance
		'''
		return simplejson.dumps(self.AsDict(), sort_keys=True)

	def AsDict(self):
		'''A dict representation of this twitter.Status instance.

		The return value uses the same key names as the JSON representation.

		Return:
			A dict representing this twitter.Status instance
		'''
		data = {}
		if self.id:
			data['id'] = self.id
		if self.screen_name:
			data['screen_name'] = self.screen_name
		if self.following is not None:
			data['following'] = self.following
		if self.followed_by is not None:
			data['followed_by'] = self.followed_by
		if self.notifications_enabled is not None:
			data['notifications_enabled'] = self.notifications_enabled
		if self.can_dm is not None:
			data['can_dm'] = self.can_dm
		if self.want_retweets is not None:
			data['want_retweets'] = self.want_retweets
		if self.marked_spam is not None:
			data['marked_spam'] = self.marked_spam
		if self.all_replies is not None:
			data['all_replies'] = self.all_replies
		if self.blocking is not None:
			data['blocking'] = self.blocking
		return data

class Relationship(object):
	''' A class representing the relationship between two Twitter users
	'''
	def __init__(self,
				 target=None,
				 source=None):
		self.target = target
		self.source = source

	@staticmethod
	def NewFromJsonDict(data):
		'''Create a new instance based on a JSON dict.

		Args:
			data:
				A JSON dict, as converted from the JSON in the twitter API

		Returns:
			A twitter.Relationship instance
		'''
		source = None
		target = None
		if 'relationship' in data:
			if 'source' in data['relationship']:
				source = RelationshipUser.NewFromJsonDict(data['relationship']['source'])
			if 'target' in data['relationship']:
				target = RelationshipUser.NewFromJsonDict(data['relationship']['target'])
		return Relationship(source = source, 
							target = target)
        
	def __str__(self):
		'''A string representation of this twitter.Relationship instance.

		The return value is the same as the JSON string representation.

		Returns:
			A string representation of this twitter.Relationship instance.
		'''
		return self.AsJsonString()

	def AsJsonString(self):
		'''A JSON string representation of this twitter.Relationship instance.

		Returns:
			A JSON string representation of this twitter.Relationship instance
		'''
		return simplejson.dumps(self.AsDict(), sort_keys=True)

	def AsDict(self):
		'''A dict representation of this twitter.Status instance.

		The return value uses the same key names as the JSON representation.

		Return:
			A dict representing this twitter.Status instance
		'''
		data = {}
		if self.source:
			data['source'] = self.source.AsDict()
		if self.target:
			data['target'] = self.target.AsDict()
		return data    

# new function on class Api

def ShowFriendships(self,
					source_id=None,
					source_screen_name=None,
					target_id=None,
					target_screen_name=None):
	'''Returns detailed information about the relationship between two users.

	Either source_id or source_screen_name must be supplied if the
	request is not unauthenticated.

	Args:
		source_id: The user_id of the subject user. [semi-optional, see above]
		source_screen_name: 
			The screen_name of the subject user. [semi-optional, see above]
		target_id: 
			The user_id of the target user. [one of target_id or 
			target_screen_name required]
		target_screen_name: 
			The screen_name of the target user. [one of target_id or 
			target_screen_name required]
	Returns:
		A Relationship instance.
    '''
	url = '%s/friendships/show.json' % self.base_url
	if not self._Api__auth and not source_id and not source_screen_name:
		raise TwitterError("Source must be specified if not authenticated.")
	parameters = {}
	if source_id:
		parameters['source_id'] = source_id
	if source_screen_name:
		parameters['source_screen_name'] = source_screen_name
	if target_id:
		parameters['target_id'] = target_id
	if target_screen_name:
		parameters['target_screen_name'] = target_screen_name
	json = self._RequestUrl(url, 'GET', data=parameters)
	data = self._ParseAndCheckTwitter(json.content)
	#print data
	return Relationship.NewFromJsonDict(data)
