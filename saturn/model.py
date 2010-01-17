# The MIT License
# 
# Copyright (c) 2010 Nicholas A. Granado
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to 
# deal in the Software without restriction, including without limitation 
# the rights to use, copy, modify, merge, publish, distribute, sublicense, 
# and/or sell copies of the Software, and to permit persons to whom the 
# Software is furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER 
# DEALINGS IN THE SOFTWARE.

import datetime
from google.appengine.ext import db
from google.appengine.api import memcache

from saturn import constants

class Entry(db.Model):
	id = db.IntegerProperty()
	title = db.StringProperty(required=True)
	body = db.TextProperty(required=True)
	slug = db.StringProperty(required=True)
	author = db.StringProperty(required=True)
	published = db.BooleanProperty(required=True, default=False)
	# datetime fields
	date = db.DateTimeProperty(auto_now_add=True)
	last_modified = db.DateTimeProperty(auto_now=True)
	tags = db.ListProperty(db.Category)
	
	@classmethod
	def convert_string_tags(cls, tags):
		new_tags = []
		for t in tags:
			if type(t) == db.Category:
				new_tags.append(t)
			else:
				new_tags.append(db.Category(unicode(t)))
		return new_tags
	
	def convert_to_timestamp_short(self):
		return self.date.replace(tzinfo=constants.UTC).astimezone(constants.TIMEZONE).strftime('%m/%d/%Y %H:%M')
	
	def convert_to_timestamp(self):
		return self.date.replace(tzinfo=constants.UTC).astimezone(constants.TIMEZONE).strftime('%A, %B %d, %Y %I:%M %p')
	
	def convert_to_datetime(self, timestamp):
		return datetime.datetime.strptime(timestamp, '%A, %B %d, %Y %I:%M %p').replace(tzinfo=constants.TIMEZONE).astimezone(constants.UTC)
	
	def convert_to_rfc3339(self, date):
	    return date.strftime('%Y-%m-%dT%H:%M:%SZ')
	
	def save(self):
		try:
			obj_id = self.key().id()
			resave = False
		except db.NotSavedError:
			"""
			Exception cause there is no ID on this object yet. Set a flag, to
			re-save and then finally grab the id out of the key. This is balls.
			"""
			resave = True
		self.put()
		if resave:
			self.id = self.key().id()
			self.put()
	
	def __unicode__(self):
		return self.__str__()
	
	def __str__(self):
		return '[%s] %s' % (self.date.strftime('%Y/%m/%d %H:%M'), self.title)

class EntryDataAccess():
	#@staticmethod
	def get_by_id(self, id):
		entry = db.Query(Entry).filter('id =', id).get()
		entry.permalink = "/entry/%s" % (entry.slug)
		entry.tag_string = ', '.join(entry.tags)
		entry.date_string = entry.convert_to_timestamp()
		return entry
	
	def get_by_slug(self, slug):
		entry = db.Query(Entry).filter('slug =', slug).get()
		entry.permalink = "/entry/%s" % (entry.slug)
		entry.tag_string = ', '.join(entry.tags)
		entry.date_string = entry.convert_to_timestamp()
		return entry
	
	def get_all_years_published(self):
		years = []
		for entry in self.get_all_published():
			if entry.date.year in years:
				continue
			else:
				years.append(entry.date.year)
		return years
	
	def get_all_years(self):
		years = []
		data = memcache.get("years")
		if data is not None:
			years = [y.strip() for y in data.split(',')]
		else:
			for entry in self.get_all():
				year = str(entry.date.year)
				if year in years:
					continue
				else:
					years.append(year)
			if len(years) == 0:
				year = str(datetime.datetime.utcnow().year)
				years.append(year)
			data = ','.join(years)
			memcache.add("years", data, 3600)
		return years
	
	def get_all_by_year_god(self, year):
		year = int(year)
		start_date = datetime.datetime(year, 1, 1, 12, 00, 00)
		end_date = datetime.datetime(year, 12, 31, 23, 59, 59)
		entries = db.Query(Entry).filter('date >=', start_date).filter('date <=', end_date).order('-date').fetch(constants.FETCH_THEM_ALL)
		for entry in entries:
			entry.date_string = entry.convert_to_timestamp_short()
			entry.permalink = "/entry/%s" % (entry.slug)
		return entries
	
	def get_all_for_month(self, year, month):
		start_date = datetime.date(year, month, 1)
		if start_date.month == 12:
			next_year = start_date.year + 1
			next_month = 1
		else:
			next_year = start_date.year
			next_month = start_date.month + 1

		end_date = datetime.date(next_year, next_month, 1)
		return db.Query(Entry).filter('published = ', True).filter('date >=', start_date).filter('date <', end_date).order('-date').fetch(constants.FETCH_THEM_ALL)

	def get_published_with_limit(self, limit):
		entries = db.Query(Entry).order('-date').filter('published = ', True).fetch(limit=limit)
		for entry in entries:
			entry.date_string = entry.convert_to_timestamp()
			entry.permalink = "/entry/%s" % (entry.slug)
		return entries
	
	def get_atom_feed(self, limit):
		entries = db.Query(Entry).order('-date').filter('published = ', True).fetch(limit=limit)
		for entry in entries:
			entry.permalink = "%s/entry/%s" % (constants.BLOG_URL, entry.slug)
			entry.date_string = entry.convert_to_rfc3339(entry.date)
			entry.last_modified_string = entry.convert_to_rfc3339(entry.last_modified)
		return entries

	def get_archives(self):
		entries = db.Query(Entry).order('-date').filter('published = ', True).fetch(constants.FETCH_THEM_ALL)
		for entry in entries:
			entry.date_string = entry.convert_to_timestamp()
			entry.permalink = "/entry/%s" % (entry.slug)
		return entries

	def get_all_with_short_timestamp(self):
		entries = self.get_all()
		for e in entries:
			e.date_string = e.convert_to_timestamp_short()
		return entries

	def get_all(self):
		return db.Query(Entry).order('-date').fetch(constants.FETCH_THEM_ALL)

	def get_all_published(self):
		return db.Query(Entry).filter('published =', True).order('-date').fetch(constants.FETCH_THEM_ALL)

	def get_all_tags(self):
		tag_counts = {}
		for entry in self.get_all_published():
			for tag in entry.tags:
				tag = unicode(tag)
				try:
					tag_counts[tag] += 1
				except KeyError:
					tag_counts[tag] = 1
		return tag_counts

	def get_all_published_datetimes(self):
		dates = {}
		for entry in self.get_all_published():
			date = datetime.datetime(entry.date.year, entry.date.month, entry.date.day)
			try:
				dates[date] += 1
			except KeyError:
				dates[date] = 1
		return dates

	def get_all_datetimes(self):
		dates = {}
		for entry in self.get_all():
			date = datetime.datetime(entry.date.year, entry.date.month, entry.date.day)
			try:
				dates[date] += 1
			except KeyError:
				dates[date] = 1
		return dates

	def get_all_for_month(self, year, month):
		start_date = datetime.date(year, month, 1)
		if start_date.month == 12:
			next_year = start_date.year + 1
			next_month = 1
		else:
			next_year = start_date.year
			next_month = start_date.month + 1

		end_date = datetime.date(next_year, next_month, 1)
		return db.Query(Entry).filter('published = ', True).filter('date >=', start_date).filter('date <', end_date).order('-date').fetch(constants.FETCH_THEM_ALL)

	def get_all_for_tag(self, tag):
		return db.Query(Entry).filter('published = ', True).filter('tags = ', tag).order('-date').fetch(constants.FETCH_THEM_ALL)
