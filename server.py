#!/usr/bin/python

# 20051205
# zignig@interthingy.com
# xmlrpc server for network rendering of blender files

"""
Blender shunting yard

provides a state machine for processing and rendering blender 
files and frames.
"""

from SimpleXMLRPCServer import *
import string,os,base64,sha,copy,time,httplib
import commands,pickle,threading,shutil
import ConfigParser
import StringIO


import boxomatic

# banner
global banner
global opt
banner = """
                Box-o-matic
                box builder
                tigger@interthingy.com
                201004261020
	"""

# config template for server
template = {
		'global': [
				('address to listen on','address','*'),
				('server name for url','servername','localhost'),
				('server port to listen on','port','8082'),
				]

		}

def get_config(file_name,template):
	cf = ConfigParser.SafeConfigParser()
	sections = template.keys()
	print 'Checking for config file'
	try:
			os.stat(file_name)
			print 'Config Exists'
	except:
			print 'No Config file, please enter details'
			for i in sections:
					print
					print '\tSection : '+i
					cf.add_section(i)
					for j in template[i]:
							value = raw_input(j[0]+' ( default:'+j[2]+' ) : ')
							if value == '':
									cf.set(i,j[1],j[2])
							else:
									cf.set(i,j[1],value)
			f = open(file_name,'w')
			print
			print 'Writing Config File'
			cf.write(f)
			f.close()
			print 'Finished writing config file'
	try:
			f = open(file_name)
			cf.readfp(f)
	except:
			print 'config broken'
	return cf

# file encoder 

# html services 

global style_sheet 

print "loading style sheet"
try:
	os.stat('stylesheet.css')
	f = open('stylesheet.css')
	style_sheet = f.read()
	f.close()	
except:
	print ' no style sheet '
	style_sheet = ''

class shunthtml:
	def __init__(self):
		self.status = 1
	
	def respond_svg(self):
                reload(boxomatic)
		response = boxomatic.box_maker()
		return response

	def respond(self):
		response = """
			<html><head>
			<title>Box-o-matic</title>
			<link rel=stylesheet href=/css type=text/css>
			</head><body>
			<div id=banner>
			<h1>Box-o-matic</h1>
			</div>
		"""
		#response = response + self.list_objects()
		d = vars(self.opt).keys()
		entry = vars(self.opt)
		#d.sort()
		response = response + '<a href="just_svg">Just SVG</a>'
		response = response + '<table><tr valign="top"><td>'
		for i in d:
			response = response + '<tr>'
			response = response + '<td align="right"><form action="set">'
			response = response + i
			response = response + '</td><td><input name="'+i+'" value="'+str(entry[i]) + '">' + '\n'
			response = response + '</form>'
			response = response + '</td></tr>'
		response = response + '</td></table>'
		response = response + '</td><td>'
		response = response + '<div float="right">'
		response = response + '<embed src="./svg " name="box" type="image/svg+xml" />'
		response = response + '</td></tr></table>'
		response = response + '</div>'
		response = response + '</body></html>'
		return response

class requesth(SimpleXMLRPCRequestHandler):
	" html responder for the server"

	global stylesheet , opt
	
	
	def do_GET(self):
		tmp = string.split(self.path,'/')[1:]
		print self.path 
		query = string.split(self.path,'?')
		print '-----> PATH ' + str(query)
		if len(query) > 1:
			if query[0] == '/set':
				data = string.split(query[1],'=')
				if len(data) == 2:
					print 'yay' + str(data)
					vars(opt)[data[0]] = float(data[1])
					

		print self.client_address
		print self.requestline
		self.server.action(tmp)
		if tmp[0] == 'css':
			# return style sheet
			response = style_sheet 
			self.send_response(200)
			self.send_header("Content-type", "text/css")
			self.send_header("Content-length", str(len(response)))
			self.end_headers()
			self.wfile.write(response)
		elif tmp[0] == 'just_svg':
			response = self.server.respond_svg() 
			self.send_response(200)
			self.send_header("Content-type", "application/svg+xml")
			self.send_header("Content-length", str(len(response)))
			self.end_headers()
			self.wfile.write(response)
		elif tmp[0] == 'svg':
			response = self.server.respond_svg() 
			self.send_response(200)
			self.send_header("Content-type", "image/svg+xml")
			self.send_header("Content-length", str(len(response)))
			self.end_headers()
			self.wfile.write(response)
		elif tmp[0]  == 'set':
			print "setting variables"
			print self.path
		else:
			response = self.server.respond() 
			self.send_response(200)
			self.send_header("Content-type", "text/html")
			self.send_header("Content-length", str(len(response)))
			self.end_headers()
			self.wfile.write(response)
		# shut down the connection
		self.wfile.flush()
		#self.connection.shutdown(1)

class rpcs(SimpleXMLRPCServer,shunthtml):
	def __init__(self,addr,shunt,requestHandler=requesth,logRequests=1):
		SimpleXMLRPCServer.__init__(self,addr,requestHandler,logRequests)
		shunthtml.__init__(self)
		self.opt = opt 

	def action(self,tmp):
		print 'go'

class blender_server:
	global banner

	" class to expose to xmlrpc server " 
	def __init__(self,s,secret):
		" create the render server object " 
		# set up local variables
	def bork(self):
		return 'bork'

	
		
class render_thread(threading.Thread):
	" seperate thread that runs the xmlrpc server " 
	def run(self):
		print "running server"
		# open xmlrpc server
		server = rpcs((self.name,self.port),self.opt)
		print 'registering funtions'
		server.register_instance(blender_server('',''))
		server.register_introspection_functions()
		print 'serving on ' ,self.port
		server.serve_forever()

def render_server(opt,server_name,port,secret):
	" creates and starts a render server " 
	thr = render_thread()
	thr.name = server_name
	thr.secret = secret
	thr.port = port
	thr.opt = opt 
	thr.setDaemon(1)
	thr.start()

def main():
	" main server starter " 
	global s
	global opt
	opt = boxomatic.config()
	print banner
	cf = get_config('serverconfig.cfg',template)
	# import from config
	server_name  = ''
	port = int(cf.get('global','port'))
	render_server(opt,server_name,port,'')
	while(1):
		time.sleep(3)

if __name__ == "__main__":
	main()
