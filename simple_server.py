#!/usr/bin/python
#
# run as root

import time
import BaseHTTPServer
import socket

host_name = socket.gethostname()
if '.local' not in host_name: host_name = host_name + '.local'
HOST_NAME = socket.gethostbyname(host_name) 
PORT_NUMBER = 8080 # non-root web server


class MyHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_HEAD(s):
        s.send_response(200)
        s.send_header("Content-type", "text/html")
        s.end_headers()
    def do_GET(self):
		try:
			print "requested path: " + self.path
			
			if self.path=="/":
				self.path="./test.html"
			
			sendReply = True
			if self.path.endswith(".html"):
				mimetype='text/html'
				sendReply = True
			elif self.path.endswith(".jpg"):
				mimetype='image/jpg'
				sendReply = True
			elif self.path.endswith(".gif"):
				mimetype='image/gif'
				sendReply = True
			elif self.path.endswith(".js"):
				mimetype='application/javascript'
				sendReply = True
			elif self.path.endswith(".css"):
				mimetype='text/css'
				sendReply = True
			
# 			"""Respond to a GET request."""
# 			s.send_response(200)
# 			s.send_header("Content-type", mimetype)
# 			s.end_headers()
# 			file = './deleteme.html'
# 			page = open(file)
# 			s.wfile.write(page.read())
# 			page.close()
			
			if sendReply == True:
				#Open the static file requested and send it
				f = open(self.path) 
				self.send_response(200)
				self.send_header('Content-type',mimetype)
				self.end_headers()
				self.wfile.write(f.read())
				f.close()
			return
			
		except IOError:
			self.send_error(404,'Python File Not Found: %s' % self.path)
#		except KeyboardInterrupt:
#			print '^C received, shutting down the web server'
#			server.socket.close()
	

if __name__ == '__main__':
    server_class = BaseHTTPServer.HTTPServer
    httpd = server_class((HOST_NAME, PORT_NUMBER), MyHandler)
    print time.asctime(), "Server Starts - %s:%s" % (HOST_NAME, PORT_NUMBER)
    try:
        httpd.serve_forever()
#    except KeyboardInterrupt:
#        pass
    except KeyboardInterrupt:
        print 'Recieved ^C ... exiting'
    except:
	print 'Error ... exiting'
    httpd.server_close()
    print time.asctime(), "Server Stops - %s:%s" % (HOST_NAME, PORT_NUMBER)
