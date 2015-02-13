#!/usr/bin/env python

from libnmap.process import NmapProcess
from libnmap.parser import NmapParser
import pprint as pp
import datetime
from awake import wol

# determine OS
from sys import platform as _platform
'''
Format:

{'xx:xx:xx:xx:xx:xx': {'hostname': 'unknown',
                       'ipv4': '192.168.12.x',
                       'lastseen': '20150208-21:06',
                       'ports': {53: '[tcp]domain',
                                 137: '[udp]netbios-ns',
                                 139: '[tcp]netbios-ssn',
                                 445: '[tcp]microsoft-ds',
                                 548: '[tcp]afp',
                                 5009: '[tcp]airport-admin',
                                 5353: '[udp]zeroconf',
                                 10000: '[tcp]snet-sensor-mgmt'},
                       'status': 'up',
                       'type': 'Apple'},
 'xx:xx:xx:xx:xx:xx': {'hostname': 'unknown',
                       'ipv4': '192.168.12.x',
                       'lastseen': '20150208-21:06',
                       'ports': {5000: '[tcp]upnp', 5353: '[udp]zeroconf'},
                       'status': 'up',
                       'type': 'Apple'},
 'xx:xx:xx:xx:xx:xx': {'hostname': 'unknown',
                       'ipv4': '192.168.12.x',
                       'lastseen': '20150208-21:06',
                       'ports': {5000: '[tcp]upnp', 5353: '[udp]zeroconf'},
                       'status': 'up',
                       'type': 'Apple'}}
'''

# get local host info
import re
import uuid
import socket

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
		host_name = socket.gethostname()
		if '.local' not in host_name: host_name = host_name + '.local'
		ip = socket.gethostbyname(host_name)
		return ip

	"""
	Major flaw doesn't allow you to get the localhost's MAC address
	in: none
	out: string of hex for MAC address 'aa:bb:11:22..'
	"""
	def getHostMAC(self):
		return  ':'.join(re.findall('..', '%012x' % uuid.getnode()))

'''
PORT     STATE         SERVICE
22/tcp   open          ssh
88/tcp   open          kerberos-sec
548/tcp  open          afp
88/udp   open|filtered kerberos-sec
123/udp  open          ntp
137/udp  open|filtered netbios-ns
138/udp  open|filtered netbios-dgm
5353/udp open|filtered zeroconf
'''
class NetworkScan:
	def __init__(self):
		self.this_host = IP()
		
	def nmap_cmd(self,tgt,cmd):
		nmap_proc = NmapProcess(targets=tgt,options=cmd)
		nmap_proc.run()
		xml_msg = nmap_proc.stdout
		nmap_report = NmapParser.parse(xml_msg)
		return nmap_report
		
		
	"""
	Use the avahi (zeroconfig) tools to find a host name ... this only works
	on Linux using the avahi tools.
	
	in: ip
	out: string w/ host name
	"""
	def getHostName(self,ip):
		name = 'unknown'
		if _platform == 'linux' or _platform == 'linux2':
			cmd = ["avahi-resolve-address %s | awk '{print $2}'"%(ip)]
			name  = self.runProcess(cmd)
			name = name.rstrip()
			if name == '': name = 'unknown'
		return name
		
	'''
	Options:
	   -sn disable port check
	Common ports open on my Apple computers for things
	PORT     STATE         SERVICE
	22/tcp   open          ssh
	88/tcp   open          kerberos-sec
	548/tcp  open          afp
	88/udp   open|filtered kerberos-sec
	123/udp  open          ntp
	137/udp  open|filtered netbios-ns
	138/udp  open|filtered netbios-dgm
	5353/udp open|filtered zeroconf
	'''
	def ping(self,tgts):
		nmap_report = self.nmap_cmd(tgts,"-sn -PS22,80,88,123,443,548,5009,5353")
		hosts = nmap_report.hosts
		
		up = []
		for host in hosts:
			if host.is_up():
				up.append(host.id)
		return up
	
	'''
	Options:
	   -sS TCP sync check
	   -sU UDP check
	   -F  fast check
	'''
	def portScan(self,ip):
		nmap_report = self.nmap_cmd(ip,"-sS -sU -F")
		hosts = nmap_report.hosts
		for host in hosts:
			p={}
			#print host.hostnames, host.id, host.mac, host.vendor, ' up:', host.is_up()
			for serv in host.services:
				#print serv.port,serv.protocol,serv.service
				if serv.open(): p[ str(serv.port) ] = '[' + serv.protocol + ']' + serv.service
			
			val = {'ipv4': ip, 'hostname': 'unknown', 'ports': p, 'status': 'up', 'type': host.vendor}
			key = host.mac
		
		return key,val
	
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
		pp.pprint(up)
		hosts = dict()
		time_now = str(datetime.datetime.now().strftime('%Y%m%d-%H:%M'))
		for ip in up:
			if ip == '': continue
			#print '[+] scanning ip:',ip
			name = self.getHostName(ip)
			mac,info = self.portScan(ip)
			
			# try again
			if not mac:
				if self.this_host.ip == ip:
					mac = self.this_host.mac
				else: 
					print 'try',ip,'again'
					mac,info = self.portScan(ip)
			
			if mac == '':
				print 'Error:',ip
			else:
				info['lastseen'] = time_now
				info['hostname'] = name
				hosts[mac] = info
		
		return hosts
		
	"""
	Wake-on-lan (wol)
	in: hw addr
	out: None
	"""
	def wol(self, mac):
		wol.send_magic_packet(mac)

def main():
	n = NetworkScan()
	info = n.scanNetwork('192.168.1.1-5')
	pp.pprint(info)


if __name__ == '__main__':
	main()

