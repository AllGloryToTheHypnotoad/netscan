# Network Scanner

![diagram](./pics/LAN Scanner 3.png)

Simple python script which uses [nmap](http://) and [avahi](http://www.avahi.org) to:

1. Find hosts that are on the LAN, uses WOL
2. Scan each host to determine: open ports, OS info, MAC address
3. Notify admin of new hosts on network
4. Store record of hosts in YAML file

## Usage

Scanner:

	sudo netscan

Web server (http://localhost:9000):

	simple_server

## UNIX Tools

Install:

	OSX: brew install nmap
	Linux: sudo apt-get install nmap

	sudo pip install twilio wol PyYAML

Nmap needs to be run as root, using sudo, to do it's job properly.

	???

Nmap network scan:

	sudo nmap -sn -PS22,80,443,3389,5000 -oG - %s 

* `sn` is no port scan, this is the old `sP` arg
* `P` are a listing of select ports
* `G` is grepable output

Nmap host scan:

	nmap -sS -oN - _host-IP_

* `sS` is ...
* `oN` is normal output

**Note:** Both `nmap` commands get pipped through grep, awk, and/or sed to clean the output up for python.

## Data Base

Currently this is just a simple python dictionary which gets stored on the hard drive as a YAML file.

	00:21:5A:FE:BC:4A:
	  hostname: unknown
	  ipv4: 192.168.1.90
	  ports: {'10000': snet-sensor-mgmt, '1026': LSA-or-nterm, '23': telnet, '427': svrloc,
		'515': printer, '5357': wsdapi, '80': http, '9100': jetdirect}
	  status: up
	  type: (Hewlett-Packard

## Notification

Admin notification is via [Twilio](http://)

## Environment

This program runs on both linux (Raspberry Pi) and OSX.

