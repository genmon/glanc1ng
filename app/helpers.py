from dateutil import relativedelta
from datetime import datetime

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
	one_day = 24 * one_hour
	
	energy = 0
	
	# +1 for you glancing in the last 60 minutes
	if last_sent_glance is not None and (now - last_sent_glance).seconds < one_hour:
		energy +=1
	
	within_hour = [True for (s, w) in received_glances
					if w is not None and (now - w).seconds < one_hour]
	within_day = [True for (s, w) in received_glances
					if w is not None and (now - w).seconds < one_day]
	
	# +1 for one other glancing in the last 24 hours
	if len(within_day) > 0:
		energy += 1
	
	# +1 for one other glancing in the last 60 minutes, or >1 in the last 24
	if len(within_hour) > 0 or len(within_day) > 1:
		energy += 1
	
	# +1 for all others glancing in the last 60 minutes
	if len(within_hour) == len(received_glances):
		energy += 1
	
	assert energy in [0, 1, 2, 3, 4]
	return energy
	
def time_ago_human_readable(dt=None):
	now = datetime.utcnow()
	
	ago_string = None
	if dt is None:
		ago_string = "You've never noticed %s glance at you"
	else:
		attrs = ['years', 'months', 'days', 'hours', 'minutes']
		human_readable = lambda delta: [
		    '%d %s' % (getattr(delta, attr), getattr(delta, attr) > 1 and attr or attr[:-1]) 
		        for attr in attrs if getattr(delta, attr)
		]

		r = relativedelta.relativedelta(now, dt)
		
		if r.years > 0 or r.months > 0:
			ago_string = "%s last glanced at you over a month ago."
		
		ago_suffix = ""
		if r.days > 0:
			if r.hours == 0:
				ago_suffix = "%d days ago" % r.days
			else:
				ago_suffix = "%d days and %d hours ago" % (r.days, r.hours)
		elif r.hours > 0:
			if r.minutes == 0:
				ago_suffix = "%d hours ago" % r.hours
			else:
				ago_suffix = "%d hours and %d minutes ago" % (r.hours, r.minutes)
		else:
			ago_suffix = "%d minutes ago" % r.minutes
		
		ago_string = "%s last glanced at you " + ago_suffix
	
	return ago_string
