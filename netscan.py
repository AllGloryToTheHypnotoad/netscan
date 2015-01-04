#!/usr/bin/env python

import subprocess
#import nmap << junk
from awake import wol

import time
 
import json
import yaml
import datetime

import pprint as pp

# determine OS
from sys import platform as _platform

# get local host info
import re
import uuid
import socket

# sudo fing --silent -s 192.168.1.2 -o json
#  fping -a -q  -s -g 192.168.1.0/24

"""
don't trust hardware addrss ... see below
[kevin@Tardis fping]$ sudo fing --silent -r 1  -o table,csv
192.168.1.1;;up;;;6C:70:9F:CE:DA:85; <<<
192.168.1.2;;up;;;6C:70:9F:CE:DA:85; <<<
192.168.1.3;;up;;;6C:70:9F:CE:DA:85; <<<
192.168.1.4;;up;;;F8:1E:DF:EA:68:20;Apple
192.168.1.5;;up;;;5C:95:AE:93:2F:A5;Apple
192.168.1.6;;up;;;40:30:04:F0:8C:5A;Apple
192.168.1.9;;up;;;90:B9:31:EC:AA:46;
192.168.1.13;;up;;;C8:2A:14:1F:18:69;Apple
192.168.1.14;;up;;;78:7E:61:CB:2B:52;
192.168.1.17;;up;;;B8:27:EB:0A:5A:17;Raspberry Pi Foundation
192.168.1.18;;up;;;6C:70:9F:CE:DA:85; <<<
192.168.1.19;;up;;;AC:FD:EC:74:E7:7B;
192.168.1.20;;up;;;B4:18:D1:3F:6B:F4;
192.168.1.21;;up;;;8C:2D:AA:8D:D7:DD;
192.168.1.23;;up;;;8C:2D:AA:75:EE:3B;
192.168.1.90;;up;;;00:21:5A:FE:BC:4A;HP
"""


class IP:
	ip = 'x'
	mac = 'x'
	
	def __init__(self):
		self.mac = self.getHostMAC()
		self.ip = self.getHostIP()
		
	"""
	Need to get the localhost IP address 
	in: none
	out: returns the host machine's IP address
	"""
	def getHostIP(self):
		ip = socket.gethostbyname(socket.gethostname())
		return ip

	"""
	Major flaw doesn't allow you to get the localhost's MAC address
	in: none
	out: string of hex for MAC address 'aa:bb:11:22..'
	"""
	def getHostMAC(self):
		return  ':'.join(re.findall('..', '%012x' % uuid.getnode()))
	
# 	"""
# 	 Only need the first 3 parts of the IP address
# 	 TODO: change name, sucks!
# 	"""
# 	def getNetwork(self):
# 		ip = socket.gethostbyname(socket.gethostname())
# 		i=ip.split('.')
# 		ip = i[0]+'.'+i[1]+'.'+i[2]+'.'
# 		return ip

this_host = IP()

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
			print 'ioerror'
		return file
		
	def write(self,filename,data):
		f = open(filename,'w')
		yaml.safe_dump(data,f)
		f.close()
		
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

"""
Simple python wrapper around nmap and fping to scan and collect info on
systems on my LAN. Nmap outputs info like this:

# Nmap 6.00 scan initiated Sat Dec 27 19:51:42 2014 as: nmap -oN - 192.168.1.1
Nmap scan report for 192.168.1.1
Host is up (0.0013s latency).
Not shown: 994 closed ports
PORT      STATE SERVICE
53/tcp    open  domain
139/tcp   open  netbios-ssn
445/tcp   open  microsoft-ds
548/tcp   open  afp
5009/tcp  open  airport-admin
10000/tcp open  snet-sensor-mgmt
MAC Address: 6C:70:9F:CE:DA:85 (Unknown)

# Nmap done at Sat Dec 27 19:51:55 2014 -- 1 IP address (1 host up) scanned in 14.00 seconds

"""
class NetworkScan:
	def __init__(self):
		a=1
	
	"""
	in: command with args: ['some_command -a -b -c -etc']
	out: string containing the results
	"""
	def runProcess(self,cmd):
		out = subprocess.Popen(cmd, stdout = subprocess.PIPE, stderr=subprocess.PIPE, shell=True).communicate()[0]
		return out
	
	"""
	Note: probably don't need all those ports in nmap search
	in: network ip address ex: 192.168.1.0/24
	out: list of hosts ip's
	"""
	def ping(self, ip):
		print 'ping()'
		#cmd = ['fping -a -g %s'%(ip)]
		cmd = ["sudo nmap -sn -PS22,80,443,3389,5000 -oG - %s | grep Up | awk '{print $2}'"%(ip)]
		#out = subprocess.Popen(cmd, stdout = subprocess.PIPE, stderr=subprocess.PIPE, shell=True).communicate()[0]
		out = self.runProcess(cmd)
		hosts = out.split('\n')
		
		#print hosts
		
		return hosts
	"""
	Use the avahi (zeroconfig) tools to find a host name ... this only works
	on Linux.
	
	in: ip
	out: string w/ host name
	"""
	def getHostName(self,ip):
		name = 'unknown'
		if _platform == 'linux' or _platform == 'linux2':
			args = "%s"%(ip)
			cmd = ["avahi-resolve-address",args]
			#out = subprocess.Popen(["avahi-resolve-address",args], stdout = subprocess.PIPE, stderr=subprocess.PIPE, shell=True).communicate()[0]
			out = self.runProcess(cmd)
			name = out.split(' ')[1]
		return name
	
	"""
	Quick recon found hosts that were up, now doing slower port scan
	in: ip addr
	out: open tcp ports, hardware address, OS typs info
	"""
	def portScan(self, ip):
		# http://nmap.org/book/man-briefoptions.html
		# -sS TCP SYN
		# -O OS detection and hw addr
		# -F faster scan mode, fewer ports searched 
		# result is also pipped to grep where it pulls tcp or MAC lines
		# result is pipped to sed to remove extra whitespace
		cmd = ["nmap -sS -oN - %s  | grep 'tcp\|MAC' | sed 's/^ *//;s/ *$//;s/ \{1,\}/ /g' "%(ip)]
		#print 'cmd: ',cmd
		#out = subprocess.Popen(cmd, stdout = subprocess.PIPE, stderr=subprocess.PIPE, shell=True).communicate()[0]
		out = self.runProcess(cmd)
		
		#print out
		
		id = 'unknown'
		type = 'unknown'
		tcp = dict()
		
		d_out = out.split('\n')
		for line in d_out:
			#line = killws(line) - sed fixes this
			l = line.split(' ')
			if l[0] == 'MAC':
				#print 'MAC line: ',line,' len: ',len(l)
				#print 'mac: ',l[2]
				id = l[2]
				type = l[3]
			elif '/tcp' in l[0]:
				#print 'line: ',line,' len: ',len(l)
				#print 'svc: ',l[2]
				tcp[ l[0].split('/')[0] ] = l[2]
		
		#print 'nmap results: ',id,type,tcp
		
		return tcp,id,type
	
	"""
	Main network scanner function.
	 1. find hosts up
	 2. scan those for open ports & HW addr
	 3. get host name (only on linux)
	 4. return dict of hosts,name,id,ip
	
	in: network ip range, ex.: 192.168.1.0/24
	out: dict with info for each system found
	"""
	def scanNetwork(self,net):
		up = self.ping(net)
		hosts = dict()
		time_now = str(datetime.datetime.now().strftime('%Y%m%d-%H:%M'))
		for ip in up:
			if ip == '': continue
			print '[+] scanning ip:',ip
			p,hw_addr,type = self.portScan(ip)
			
			# since we finger print on hw_addr, if we don't have it move on
			# Note: there is an issue getting the mac addr, this catches it
			if hw_addr == 'unknown': 
				if ip == this_host.ip:
					hw_addr = this_host.mac
				else:
					# I find IOS devices see pings, but then don't produce anything on 
					# the port scan ... I think they are sleeping.
					print "[-] Couldn't get MAC Addr for %s"%(ip)
					continue
			
			name = self.getHostName(ip)
			hosts[hw_addr] = {'ipv4': ip, 'hostname': name, 'ports': p, 'status': 'up', 'type': type, 'last_seen': time_now}
		
		return hosts
	"""
	Wake-on-lan (wol)
	in: hw addr
	out: None
	"""
	def wol(self, mac):
		wol.send_magic_packet(mac)

"""
Send SMS notification
in: message
out: None
"""
def notify(items):
	return 0	

def main():
	
	db = Database()
	db.load('network.yaml')
	
	scan = NetworkScan()
	
	while 1:
		# wake things up
		hw_addr = db.hw_addr()
		for mac in hw_addr:
			scan.wol(mac)
		
		#print 'start scan'
		list = scan.scanNetwork('192.168.1.0/24')
		pp.pprint(list)
		
		#ans,new_items = db.diff(list)
		db.update(list)
		
		#if ans == true:
		#	notify(new_items)
		
		db.save('network.yaml')
		
		time.sleep(1)

if __name__ == '__main__':
    main()

