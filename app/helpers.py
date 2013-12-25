from dateutil import relativedelta
from datetime import datetime



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
