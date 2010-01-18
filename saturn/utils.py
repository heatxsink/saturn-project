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