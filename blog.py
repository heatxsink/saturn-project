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

import cgi, datetime

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext import db

from saturn import handlers
from saturn import constants
from saturn import model

class IndexHandler(handlers.RequestHandler):
	def get(self):
		data_access = model.EntryDataAccess()
		entries = data_access.get_published_with_limit(5)
		title = "%s - %s" % (constants.BLOG_TITLE, 'blog')
		main_page_entries = { 'page_title': title, 'blog_title': constants.BLOG_TITLE, 'feed_url': constants.FEED_URL, 'twitter_url': constants.TWITTER_URL, 'blog_description': constants.BLOG_DESCRIPTION, 'entries': entries, 'page': 'Blog'}
		self.render_to_response('blog.html', main_page_entries)

class EntryHandler(handlers.RequestHandler):
	def get(self, slug):
		if not slug:
			raise web.HTTPError(404)
		data_access = model.EntryDataAccess()
		entry = data_access.get_by_slug(slug)
		title = "%s - %s" % (constants.BLOG_TITLE, entry.title)
		entry_page = { 'page_title': title, 'blog_title': constants.BLOG_TITLE, 'feed_url': constants.FEED_URL, 'twitter_url': constants.TWITTER_URL, 'blog_description': constants.BLOG_DESCRIPTION, 'entries': [entry], 'page': 'Entry'}
		self.render_to_response('blog.html', entry_page)

class ArchiveHandler(handlers.RequestHandler):
	def get(self):
		data_access = model.EntryDataAccess()
		entries = data_access.get_archives()
		title = "%s - %s" % (constants.BLOG_TITLE, 'archive')
		archive_page = { 'page_title': title, 'blog_title': constants.BLOG_TITLE, 'feed_url': constants.FEED_URL, 'twitter_url': constants.TWITTER_URL, 'blog_description': constants.BLOG_DESCRIPTION, 'entries': entries, 'page': 'Archive'}
		self.render_to_response('blog.html', archive_page)

class AtomFeedHandler(handlers.RequestHandler):
	def get(self):
		data_access = model.EntryDataAccess()
		entries = data_access.get_atom_feed(constants.TOTAL_RECENT)
		updated = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
		if len(entries) > 0:
			updated = entries[0].last_modified_string
		title = "%s - %s" % (constants.BLOG_TITLE, constants.BLOG_DESCRIPTION)
		blog_url = constants.BLOG_URL + "/"
		favicon = "%s/favicon.ico" % (constants.BLOG_URL)
		atom_entries = { 'title' : title, 'updated' : updated, 'blog_url' : blog_url, 'entries' : entries, 'favicon' : favicon, 'author' : constants.BLOG_AUTHOR, 'feed_url' : constants.FEED_URL }
		self.response.headers['Content-Type'] = 'application/xml'
		self.render_to_response('atom.xml', atom_entries)

application = webapp.WSGIApplication([
	(r'/', IndexHandler),
	(r'/archive', ArchiveHandler),
	(r'/entry/?', ArchiveHandler),
	(r'/entry/([^/]+)', EntryHandler),
	(r'/feed', AtomFeedHandler)], debug=True)

def main():
	util.run_wsgi_app(application)

if __name__ == '__main__':
	  main()