#!/usr/bin/env python

# take a look at this:  https://pypi.python.org/pypi/python-libnmap/0.6.1

import time
import make_html5 as mh
from YamlDoc import YamlDoc
import datetime
#import pprint as pp
import NetworkScan as ns
import argparse

def makeTable(info):
	table = ['<h1> LAN Host Map </h1>']
	table.append('<style> table, tr, th { border: 1px solid gray; border-collapse: collapse;} th {background-color: #0066FF; color: white;} #porttable, #porttd { border: 0px;}</style>')
	table.append('<table style="width:100%">')
	table.append('<tr> <th> Host Name </th> <th> IPv4 </th> <th> MAC addr </th> <th> Type </th> <th> Status </th> <th> Ports </th> </tr>')
	table.append('<p> <i class="fa fa-check-circle" style="color:green"></i> Host Up </p>')
	table.append('<p> <i class="fa fa-times-circle" style="color:red"></i> Host Down </p>')
	
	time_now = str(datetime.datetime.now().strftime('%Y%m%d-%H:%M'))
	table.append('<p> Info last updated: %s </p>'%time_now)
	
	table.append('<p> A list of common TCP ports is <a href="http://en.wikipedia.org/wiki/List_of_TCP_and_UDP_port_numbers"> here </a></p>')
	
	for k,v in info.iteritems():
		table.append('<tr>')
		table.append( '<td>' + v['hostname'] + '</td>' )
		table.append( '<td>' + v['ipv4'] + '</td>' )
		table.append( '<td>' + k + '</td>' )
		table.append( '<td>' + v['type'] + '</td>' )
		
		
		#table.append( '<td>' + v['status'] + '</td>' )
		if v['status'] == 'up':
			#icon = '<i class="fa fa-chevron-circle-up"></i>'
			icon = '<i class="fa fa-check-circle" style="color:green"></i>'
		else:
			#icon = '<i class="fa fa-chevron-circle-down"></i>'
			icon = '<i class="fa fa-times-circle" style="color:red"></i>'
			
		table.append( '<td>' + icon + '</td>' )
		
		# do a table within a table for all of the ports
		table.append('<td><table id="porttable">')
		for a,b in v['ports'].iteritems():
			table.append( '<tr id="porttd"><td>' + a + '</td><td>' + b + '</td></tr>' )
		
		table.append('</table></td>')
		table.append('</tr>')
		
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
	parser = argparse.ArgumentParser('A simple network recon program')
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

