from datetime import timedelta



def get_natural_str(delta):
	"""
	Returns a natural string representing the given timedelta. The biggest unit
	is the hour, because a working day is too ambiguous.
	"""
	d = {}
	
	d['minutes'], d['seconds'] = divmod(int(delta.total_seconds()), 60)
	d['hours'], d['minutes'] = divmod(d['minutes'], 60)
	
	li = []
	
	for unit in ('hours', 'minutes', 'seconds'):
		if d[unit]:
			s = str(d[unit])+' '+unit
			if d[unit] == 1:
				s = s[:-1]
			li.append(s)
	
	return ', '.join(li)



