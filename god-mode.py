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

import cgi, datetime, re

from google.appengine.api import memcache
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util

from saturn import named_entities
from saturn import handlers
from saturn import constants
from saturn import model

class IndexEntriesHandler(handlers.RequestHandler):
	def get(self):
		data_access = model.EntryDataAccess()
		years = data_access.get_all_years()
		year = years[0]
		entries = data_access.get_all_by_year_god(year)
		list_entries = {'entries' : entries, 'blog_title' : constants.BLOG_TITLE, 'years' : years, 'year' : year}
		self.render_to_response('god-mode.html', list_entries)

class ListEntriesHandler(handlers.RequestHandler):
	def get(self, year):
		data_access = model.EntryDataAccess()
		years = data_access.get_all_years()
		entries = data_access.get_all_by_year_god(year)
		list_entries = {'entries' : entries, 'blog_title' : constants.BLOG_TITLE, 'years' : years, 'year' : year}
		self.render_to_response('god-mode.html', list_entries)

class CreateEntryHandler(handlers.RequestHandler):
	def get(self):
		entry = model.Entry(title='title goes here', body='content goes here', slug='slug-goes-here', author=constants.BLOG_AUTHOR, published=False)
		entry.date_string = entry.convert_to_timestamp()
		entry.tag_string='tags, go, here'
		create_entry = {'entry' : entry, 'blog_title' : constants.BLOG_TITLE}
		self.render_to_response('god-mode-entry.html', create_entry)

class ReadEntryHandler(handlers.RequestHandler):
	def get(self, heater_id):
		id = int(heater_id)
		data_access = model.EntryDataAccess()
		entry = data_access.get_by_id(id)
		#entry.body = entry.body
		if not entry:
			raise ValueError, 'Entry with ID %d does not exist.' % id
		title = "%s - %s" % (constants.BLOG_TITLE, entry.title)
		preview_entry = { 'page_title': title, 'blog_title': constants.BLOG_TITLE, 'feed_url': constants.FEED_URL, 'twitter_url': constants.TWITTER_URL, 'blog_description': constants.BLOG_DESCRIPTION, 'entries': [entry], 'page': 'Entry'}
		self.render_to_response('blog.html', preview_entry)

class UpdateEntryHandler(handlers.RequestHandler):
	def post(self):
		id = self.request.get('heater_id')
		title = self.request.get('heater_title')
		body = self.request.get('heater_body')
		tags = self.request.get('heater_tags')
		date = self.request.get('heater_date')
		slug = self.request.get('heater_slug')
		old_slug = self.request.get('heater_old_slug')
		author = self.request.get('heater_author')
		published = self.request.get('heater_published')
		
		if tags:
			tags = [t.strip() for t in tags.split(',')]
		else:
			tags = []
		tags = model.Entry.convert_string_tags(tags)
		
		if published == 'on':
			published = True
		else:
			published = False
		
		body = body.encode('ascii', 'named_entities')
		body = re.sub('&(?!([a-zA-Z0-9]+|#[0-9]+|#x[0-9a-fA-F]+);)', '&amp;', body)
		data_access = model.EntryDataAccess()
		if id != 'None':
			# it's an edit of an existing item.
			entry = data_access.get_by_id(int(id))
			entry.title = title
			entry.body = body
			entry.tags = tags
			entry.published = published
			entry.author = author
			entry.slug = slug
			if old_slug == None:
				entry.old_slug = None
			else:
				entry.old_slug = old_slug
			entry.date = entry.convert_to_datetime(date)
		else:
			# this is a new entry with no id
			entry = model.Entry(title=title, body=body, tags=tags, author=author, slug=slug, published=published)
			if old_slug == None:
				entry.old_slug = None
			else:
				entry.old_slug = old_slug
			entry.date = entry.convert_to_datetime(date)
		#
		# finally save the entry
		#
		entry.save()
		#
		# lets look ahead and make sure our years list is up to date.
		#
		years = data_access.get_all_years()
		if entry.date.year not in years:
			memcache.delete('years')
		#
		# redirect to the update action
		#
		self.redirect('/god-mode/entry/update/%s' % entry.id)
	
	def get(self, heater_id):
		id = int(heater_id)
		data_access = model.EntryDataAccess()
		entry = data_access.get_by_id(id)
		if not entry:
			raise ValueError, 'blog entry with id:%d does not exist.' % id
		edit_entry = {'entry' : entry, 'blog_title' : constants.BLOG_TITLE}
		self.render_to_response('god-mode-entry.html', edit_entry)

class DeleteEntryHandler(handlers.RequestHandler):
	def get(self, heater_id):
		id = int(heater_id)
		data_access = model.EntryDataAccess()
		entry = data_access.get_by_id(id)
		if entry:
			entry.delete()
		self.redirect('/god-mode/')

application = webapp.WSGIApplication(
	[(r'/god-mode/?', IndexEntriesHandler),
	 (r'/god-mode/entry/list/?', ListEntriesHandler),
	 (r'/god-mode/entry/list/([^/]+)', ListEntriesHandler),
	 (r'/god-mode/entry/create/?', CreateEntryHandler),
	 (r'/god-mode/entry/read/([^/]+)', ReadEntryHandler),
	 (r'/god-mode/entry/update/?', UpdateEntryHandler),
	 (r'/god-mode/entry/update/([^/]+)', UpdateEntryHandler),
	 (r'/god-mode/entry/delete/([^/]+)', DeleteEntryHandler)], debug=True)

def main():
	util.run_wsgi_app(application)

if __name__ == '__main__':
	main()
