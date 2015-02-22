# Network Scanner

![diagram](./pics/netscan.jpg)

![diagram](./pics/LAN-Scanner-3.jpg)

**Note:** The network change detection has not been implemented yet.

Simple python script which uses [nmap](http://nmap.org) and [avahi](http://www.avahi.org) to:

1. Find hosts that are on the LAN, uses WOL
2. Scan each host to determine: open ports, OS info, MAC address
3. [todo] Notify admin of new hosts on network
4. Store record of hosts in YAML file
5. Creates a webpage for the server to display

**Note:** Since IP addresses change, the hosts are finger printed via their MAC address. The system updates open port, host name, ip address, etc, but once a MAC address is detected, it never deletes it, just updates it.

## Alternatives

* [Fing](http://www.overlooksoft.com/fing) is a great and fast network scanner, I have their app on my iPad

## Install and Usage

### Install from Git

	sudo pip install git+https://github.com/walchko/netscan#egg=netscan

### Install from Package

Download and unzip, then from inside the package:

	sudo python setup.py install

If you are working on it:

	sudo python setup.py develop

### Run

	sudo python -m netscan.netscan2

## Nmap

Nmap is the heart of this and is used for detecting both host presence on the network and open ports.

Install:

	OSX: brew install nmap
	Linux: sudo apt-get install nmap

	sudo pip install twilio wol PyYAML python-nmap

Nmap needs to be run as root, using sudo, to do it's job properly.

Nmap network scan:

	sudo nmap -sn -PS22,80,443,3389,5000 network_ip_range

* `sn` is no port scan, this is the old `sP` arg
* `P` are a listing of select ports

Nmap host scan:

	nmap -sS -sU -F host_ip

* `sS` is a TCP SYN to check for open ports
* `sU` is a UDP scan for ports
* `F`  tells nmap to do this fast and not wait as long as it could for returns 

A full listing of known ports are available on [wikipedia](http://en.wikipedia.org/wiki/List_of_TCP_and_UDP_port_numbers)

**Note:** Both `nmap` commands get pipped through grep, awk, and/or sed to clean the output up for python.

## Data Base

Currently this is just a simple python dictionary which gets stored on the hard drive as a YAML file.

	{'xx:xx:xx:xx:xx:xx': {'hostname': 'unknown',
						   'ipv4': '192.168.12.55',
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
						   'ipv4': '192.168.12.56',
						   'lastseen': '20150208-21:06',
						   'ports': {5000: '[tcp]upnp', 5353: '[udp]zeroconf'},
						   'status': 'up',
						   'type': 'Apple'},
	 'xx:xx:xx:xx:xx:xx': {'hostname': 'unknown',
						   'ipv4': '192.168.12.57',
						   'lastseen': '20150208-21:06',
						   'ports': {5000: '[tcp]upnp', 5353: '[udp]zeroconf'},
						   'status': 'up',
						   'type': 'Apple'}}


## Notification

Admin notification is via [Twilio](https://www.twilio.com/sms). You can get a free account and text phone numbers you own for free.

## Environment

This program runs on both linux (Raspberry Pi) and OSX.

