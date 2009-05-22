import urllib2
import re
from datetime import datetime
# load a JSON library
try:
	import simplejson as json
except:
	try:
		import json
	except:
		raise JSONLibraryException


# to give good errors
class JSONLibraryException(Exception):
	"""Exception raised with no JSON library can be found."""
	pass

class CountryCodes(object):
	def __init__(self):
		# load defaults
		from countriesbase import countries, lastupdate
		self.countries = countries
		self.lastupdate = lastupdate
		self.checked_for_updates = False
		self.updated_countries = False
		self.get_new_countries = False
		self.last_update_uri = "http://opencountrycodes.appspot.com/python/"
		self.last_update_regex_pattern = ".*?<p>.*?Last update: (.*?)<\/p>.*?"
		self.last_update_date_format = "%Y-%m-%d %H:%M:%S"
		self.countries_uri = "http://opencountrycodes.appspot.com/json/"

	def get_countries(self):
		return self.countries
	
	def set_countries(self, countries):
		# also update countriesbase.py?
		self.countries = countries
	
	def get_last_update(self):
		return self.lastupdate
		
	def set_last_pdate(self, lastupdate):
		# also update countriesbase.py?
		self.lastupdate = lastupdate
		
	def find_last_update(self):
		"""This is an ugly, hacky way to see when the remote database has last been updated."""
		# some caching... if we've already checked, assume we have the latest
		if (self.checked_for_updates):
			return self.get_last_update()
		else:
			html = urllib2.urlopen(self.last_update_uri).read()
			reg = re.compile(self.last_update_regex_pattern, re.I)
			dt = reg.search(html).group(1)
			d = datetime.strptime(dt, self.last_update_date_format)
			self.checked_for_updates = True
			return d
		
	def are_newer_countries(self):
		remoteDate = self.find_last_update()
		areNewer = (remoteDate > self.get_last_update())
		# if we've found a newer version, update our local timestamp
		if areNewer:
			self.set_last_update(remoteDate)
			self.get_new_countries = True
		return areNewer
		
	def update_countries(self):
		# only bother if we don't have the latest
		if (self.checked_for_updates == True and self.get_new_countries == True and self.updated_countries == False):
			jsonData = urllib2.urlopen(self.countries_uri).read()
			try:
				countries = json.loads(jsonData)
				self.set_countries(countries)
				self.updated_countries = True
			except:
				self.updated_countries = False
		
	def update(self):
		if self.are_newer_countries():
			self.update_countries()
	
	def get_country_name(self, code):
		# there's got to be a more elegant way to do this
		for item in self.get_countries():
			if item['code'] == code:
				return item['name']
		# return None if we've go through the whole list and haven't found the code passed
		return None
		
	def get_country_code(self, name):
		# there's got to be a more elegant way to do this
		for item in self.get_countries():
			# does an exact string match!
			if item['name'] == name:
				return item['code']
		# return None if we've go through the whole list and haven't found the name passed
		return None
		
	def get_country_code_list(self):
		codes = []
		for item in self.get_countries():
			codes.append(item['code'])
		return codes
		
	def get_country_name_list(self):
		names = []
		for item in self.get_countries():
			names.append(item['name'])
		return names
		
	def get_html_list(self, **kwargs):
		html = "<select"
		for key in kwargs:
			html += " %(key)s=\"%(value)s\"" % {'key': key, 'value': kwargs[key]}
		html += ">\n"
		# loop could be more elegent?
		for item in self.get_countries():
			html += "\t<option value=\"%(code)s\">%(name)s</option>\n" % {'code': item['code'], 'name': item['name']}
		html += "</option>\n"
		return html
	
	def test(self):
		new = self.are_newer_countries()
		print "Are newer countries: %s" % new
		self.update_countries()
		print "Are countries updated: %s" % self.updated_countries

