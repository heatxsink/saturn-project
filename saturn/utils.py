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

import xmlrpclib, socket

def ping_the_world(site_title, url_to_new_post):
	error = ""
	ping_urls = ['http://ping.feedburner.google.com/','http://blogsearch.google.com/ping/RPC2','http://rpc.weblogs.com/RPC2']
	for url in ping_urls:
		try:
			rpc = xmlrpclib.Server(url)
			reply = rpc.weblogUpdates.ping(site_title, url_to_new_post)
			error = reply['flerror']
			error_msg = reply['message']
		except socket.error, msg:
			error = msg
		except xmlrpclib.ProtocolError, inst:
			error = inst.errmsg
		except xmlrpclib.Fault, inst:
 			error = inst.faultString
		except:
 			error = 'Unknown error occured'