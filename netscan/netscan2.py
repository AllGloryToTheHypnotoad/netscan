#!/usr/bin/env python

# take a look at this:  https://pypi.python.org/pypi/python-libnmap/0.6.1

import time
import make_html5 as mh
from YamlDoc import YamlDoc
import datetime
#import pprint as pp
import NetworkScan as ns
import argparse # commandline
import socket # ordering

# might use these to color code port number (green for good)
good_tcp_ports = ['22',   # ssh
				  '88',   # kerberos
				  '548',  # AFP - Apple File Protocol
				  '5000'] # UPnP
good_udp_ports = ['123',  # ntp - network time protocol
				  '5353'] # bonjour/zeroconfig


def makeRow(k,v):
	"""
	Build a row of the table given k (mac address) and v (host info). 
	"""
	row = []
	row.append('<tr>')
	row.append( '<td>' + v['hostname'] + '</td>' )
	
	# up or down
	if v['status'] == 'up':
		#icon = '<i class="fa fa-chevron-circle-up"></i>'
		icon = '<i class="fa fa-check-circle" style="color:green"></i>'
	else:
		#icon = '<i class="fa fa-chevron-circle-down"></i>'
		icon = '<i class="fa fa-times-circle" style="color:red"></i>'
		
	row.append( '<td>' + icon + '</td>' )
	row.append( '<td>' + v['ipv4'] + '</td>' )
	row.append( '<td>' + k + '</td>' )
	row.append( '<td>' + v['type'] + '</td>' )
	
	
	#row.append( '<td>' + v['status'] + '</td>' )
	
	# do a table within a table for all of the ports
	row.append('<td><table id="porttable">')
	
	# colorize ports
	# a - port number
	# b - port service name and [tcp] or [udp]
	if v['status'] == 'up':
		for a,b in v['ports'].iteritems():
			if (a in good_tcp_ports and b.find('[tcp]') >= 0) or (a in good_udp_ports and b.find('[udp]') >= 0):
				row.append( '<tr id="porttd"><td style="color: rgb(0,200,0)">' + a + '</td><td style="color:rgb(0,200,0)">' + b + '</td></tr>' )
			else:
				row.append( '<tr id="porttd"><td>' + a + '</td><td>' + b + '</td></tr>' )
	else: # old data is grayed out
		for a,b in v['ports'].iteritems():
			row.append( '<tr id="porttd"><td style="color:gray">' + a + '</td><td style="color:gray">' + b + '</td></tr>' )

	
	row.append('</table></td>')
	row.append('</tr>')
	ans = ''.join(row)
	return ans

def sort_ip(info):
	"""
	Using a function in socket, sorts the IP address in order.
	"""
	ip = []
	for k,v in info.items():
		ip.append( v['ipv4'] )
	ip_sorted = sorted(ip, key=lambda item: socket.inet_aton(item))
	return ip_sorted

def search(ip,info):
	for k,v in info.items():
		if ip == v['ipv4']:
			return k,v
	raise Exception('Error: search() should not have gotten here')

def findHostName(mac,info):
	if mac in info:
		return info[mac]['hostname']
	raise Exception('Error: search() should not have gotten here')

def makeTable(info):
	table = ['<h1> LAN Host Map </h1>']
	table.append('<style> table, tr, th { border: 1px solid gray; border-collapse: collapse;} th {background-color: #0066FF; color: white;} #porttable, #porttd { border: 0px;}</style>')
	#table.append('<table style="width:100%">')
	table.append('<table class="table table-striped">')
	table.append('<tr> <th> Host Name </th> <th> Status </th> <th> MAC addr </th> <th> Type </th> <th> IPv4 </th> <th> Ports </th> </tr>')
	table.append('<p> <i class="fa fa-check-circle" style="color:green"></i> Host Up </p>')
	table.append('<p> <i class="fa fa-times-circle" style="color:red"></i> Host Down </p>')
	
	time_now = str(datetime.datetime.now().strftime('%Y%m%d-%H:%M'))
	table.append('<p> Info last updated: %s </p>'%time_now)
	
	table.append('<p> A list of common TCP ports is <a href="http://en.wikipedia.org/wiki/List_of_TCP_and_UDP_port_numbers"> here </a></p>')
	
	# get sorted IP list
	ip_sorted = sort_ip(info)
	#print ip_sorted
	
	# k - mac address
	# v - dict of host info
	#for k,v in info.iteritems():
	#	table.append( makeRow(k,v) )
	try:
		for ip in ip_sorted:
			k,v = search(ip,info)
			table.append( makeRow(k,v) )
	except:
		print 'Error in sorting IP addresses'		
		
	table.append('</table>')
	
	ans = ''.join(table)
	ans = ans.replace('(','')
	ans = ans.replace(')','')
	return ans
	



##################################################################


# """
# Simple function to eat duplicate white space
# 'hi  how    are you' -> 'hi how are you'
# in: string with extra white space
# out: string with extra white space removed
# """
# def killws(str):
# 	return re.sub(' +',' ',str)

"""
Simple database that abstracts how I store host information. The current 
setup looks like this:

58:b0:35:f2:25:d8:
  hostname: 'unknown'
  ip: 192.168.1.4
  lastseen: 20141130-21:01
  status: up
  tcp: {'22': ssh, '548': afp, '88': kerberos-sec}

Could switch to a real database, but my network is small and a flat file works fine.
"""

class Database :
	def __init__(self):
		self.db = dict()
	
	def load(self,filename):
		y = YamlDoc()
		self.db = y.read(filename)
		if (self.db) != dict:
			self.db = dict()
		
	def save(self,filename):
		y = YamlDoc()
		y.write( filename, self.db )
	
	"""
	Given new scan results, this marks first marks all hosts down, then when updated, they are marked up.
	in: dict of host info
	out: none
	"""	
	def update(self, list):
		for k,v in self.db.iteritems():
			v['status'] = 'down'
			
		for k,v in list.iteritems():
			# this is kind of sloppy, fix?
			# is the mac address in the db? yes
			if k in self.db:
				hostname = self.db[k] # grab previous name just incase it went back to unknown
				self.db[k]=v
			
				if hostname != 'unknown' and self.db[k]['hostname'] == 'unknown':
					self.db[k] = hostname
			# no - so just take whatever we have
			else:
				self.db[k]=v
	
	def diff(self,list):
		return 0,dict()
		
	def hw_addr(self):
		ans = list()
		for k in self.db:
			ans.append(k)
		return ans
		
	def getDict(self):
		out = self.db
		return out


"""
Send SMS notification
in: message
out: None
"""
def notify(items):
	return 0	

def make_webpage(info,HTML_FILE):
	table = makeTable(info)
	page = mh.WebPage()
	page.create(table,'LAN Host Map')
	page.savePage(HTML_FILE)

def handleArgs():
	parser = argparse.ArgumentParser('A simple network recon program using nmap which creates a webpage.')
	parser.add_argument('-p', '--page', help='name of webpage', default='./network.html')
	parser.add_argument('-n', '--network', help='network to scan: 10.1.1.0/24 or 10.1.1.1-10', default='192.168.1.0/24')
	parser.add_argument('-y', '--yaml', help='yaml file to store network in', default='./network.yaml')
	parser.add_argument('-s', '--sleep', help='how long to sleep between scans', default=3600)
	
	args = vars(parser.parse_args())
	
	return args

def main():
	args = handleArgs()
	YAML_FILE = str(args['yaml'])
	NETWORK = str(args['network'])
	SLEEP = int(args['sleep'])
	WEBPAGE = args['page']
	
	db = Database()
	db.load(YAML_FILE)
	
	scan = ns.NetworkScan()
	
	while 1:
		# wake things up
		hw_addr = db.hw_addr()
		for mac in hw_addr:
			scan.wol(mac)
		
		print '*'*10,'Start scan on',NETWORK,'*'*10
		list = scan.scanNetwork(NETWORK)
		#pp.pprint(list)
		
		#ans,new_items = db.diff(list)
		db.update(list)
		
		#if ans == true:
		#	notify(new_items)
		
		print '>> Save:',YAML_FILE,'<<'
		db.save(YAML_FILE)
		
		print '>> Write:',WEBPAGE,'<<'
		make_webpage( db.getDict(), WEBPAGE )
		
		time.sleep(SLEEP)

if __name__ == '__main__':
    main()

