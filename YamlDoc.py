#!/usr/bin/python
#

import yaml
"""
Simple class to read/write yaml docs to dict's
"""
class YamlDoc:	
	def read(self,filename):
		# need better testing, breaks if file missing
		try:
			f = open(filename,'r')
			file = yaml.safe_load(f)
			f.close()
		except IOError:
			file = dict()
			print '[-] YamlDoc: IOError'
		return file
		
	def write(self,filename,data):
		f = open(filename,'w')
		yaml.safe_dump(data,f)
		f.close()
		

if __name__ == '__main__':
    print 'nothing to do here ... move along, move along :)'