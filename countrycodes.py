# load a JSON library
try:
	import simplejson as json
except:
	try:
		import json
	except:
		raise JSONLibraryException

import urllib2
import re
from datetime import datetime

# to give good errors
class JSONLibraryException(Exception):
	"""Exception raised with no JSON library can be found."""
	pass

class countrycodes():
	def __init__(self):
		# load defaults
		from countriesbase import countries, lastupdate
		self.countries = countries
		self.lastupdate = lastupdate
		self.checkedForUpdates = False
		self.updatedCountries = False
		self.getNewCountries = False
		self.lastUpdateUri = "http://opencountrycodes.appspot.com/python/"
		self.lastUpdateRegexPattern = ".*?<p>.*?Last update: (.*?)<\/p>.*?"
		self.lastUpdateDateFormat = "%Y-%m-%d %H:%M:%S"
		self.countriesUri = "http://opencountrycodes.appspot.com/json/"

	def getCountries(self):
		return self.countries
	
	def setCountries(self, countries):
		# also update countriesbase.py?
		self.countries = countries
	
	def getLastUpdate(self):
		return self.lastupdate
		
	def setLastUpdate(self, lastupdate):
		# also update countriesbase.py?
		self.lastupdate = lastupdate
		
	def findLastUpdate(self):
		"""This is an ugly, hacky way to see when the remote database has last been updated."""
		# some caching... if we've already checked, assume we have the latest
		if (self.checkedForUpdates):
			return self.getLastUpdate()
		else:
			html = urllib2.urlopen(self.lastUpdateUri).read()
			reg = re.compile(self.lastUpdateRegexPattern, re.I)
			dt = reg.search(html).group(1)
			d = datetime.strptime(dt, self.lastUpdateDateFormat)
			self.checkedForUpdates = True
			return d
		
	def areNewerCountries(self):
		remoteDate = self.findLastUpdate()
		areNewer = (remoteDate > self.getLastUpdate())
		# if we've found a newer version, update our local timestamp
		if areNewer:
			self.setLastUpdate(remoteDate)
			self.getNewCountries = True
		return areNewer
		
	def updateCountries(self):
		# only bother if we don't have the latest
		if (self.checkedForUpdates == True and self.getNewCountries == True and self.updatedCountries == False):
			jsonData = urllib2.urlopen(self.countriesUri).read()
			try:
				countries = json.loads(jsonData)
				self.setCountries(countries)
				self.updatedCountries = True
			except:
				self.updatedCountries = False
		
	def update(self):
		if self.areNewerCountries():
			self.updateCountries()
	
	def getCountryName(self, code):
		# there's got to be a more elegant way to do this
		for item in self.getCountries():
			if item['code'] == code:
				return item['name']
		# return False if we've go through the whole list and haven't found the code passed
		return False
		
	def getCountryCode(self, name):
		# there's got to be a more elegant way to do this
		for item in self.getCountries():
			# does an exact string match!
			if item['name'] == name:
				return item['code']
		# return False if we've go through the whole list and haven't found the name passed
		return False
		
	def getCountryCodeList(self):
		codes = []
		for item in self.getCountries():
			codes.append(item['code'])
		return codes
		
	def getCountryNameList(self):
		names = []
		for item in self.getCountries():
			names.append(item['name'])
		return names
		
	def getHTMLList(self, **kwargs):
		html = "<select"
		for key in kwargs:
			html += " %(key)s=\"%(value)s\"" % {'key': key, 'value': kwargs[key]}
		html += ">\n"
		# loop could be more elegent?
		for item in self.getCountries():
			html += "\t<option value=\"%(code)s\">%(name)s</option>\n" % {'code': item['code'], 'name': item['name']}
		html += "</option>\n"
		return html
	
	def test(self):
		new = self.areNewerCountries()
		print "Are newer countries: %s" % new
		self.updateCountries()
		print "Are countries updated: %s" % self.updatedCountries

