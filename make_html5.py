#!/usr/bin/python

import YamlDoc as yd

class WebPage:
	def __init__(self):
		self.page = []
		
	# Note: this auto refreshes every 300 seconds.
	def create(self,html_body,title='Web Page'):
		html_start = """
		<!DOCTYPE html>
		<html>
		  <head>
			<link href="http://maxcdn.bootstrapcdn.com/font-awesome/4.1.0/css/font-awesome.min.css" rel="stylesheet">
			<title>title</title>
			<meta charset="utf-8">
			<meta http-equiv="refresh" content="300">
		  </head>
		  <body>
		"""
		
		html_end = """	
		  </body>
		</html>
		"""
		
		page = []
		page.append(html_start)
		page.append(html_body)
		page.append(html_end)
		
		self.page = page
	
	def savePage(self,filename):
		f = open(filename,'w')
		for i in self.page:
			f.write(i)
		f.close()
		
	# Expect a list containing lines of html which will create a Google Map	
	def printPage(self):
		for i in self.page:
			print i


def makeTable(info):
	table = ['<h1> LAN Host Map </h1>']
	table.append('<style> table, tr, th { border: 1px solid gray; border-collapse: collapse;} th {background-color: #0066FF; color: white;} #porttable, #porttd { border: 0px;}</style>')
	table.append('<table style="width:100%">')
	table.append('<tr> <th> Host Name </th> <th> IPv4 </th> <th> MAC addr </th> <th> Type </th> <th> Status </th> <th> Ports </th> </tr>')
	table.append('<p> <i class="fa fa-check-circle" style="color:green"></i> Host Up </p>')
	table.append('<p> <i class="fa fa-times-circle" style="color:red"></i> Host Down </p>')
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
	
def main():
	y = yd.YamlDoc()
	info = y.read('network.yaml')
	table = makeTable(info)
	page = WebPage()
	page.create(table,'LAN Host Map')
	page.savePage('test.html')
	

if __name__ == "__main__":
	main()