import pcapy


# list all the network devices
pcapy.findalldevs()

max_bytes = 1024
promiscuous = False
read_timeout = 100 # in milliseconds
pc = pcapy.open_live("name of network device to capture from", max_bytes, promiscuous, read_timeout)

pc.setfilter('tcp')
dumper = pc.dump_open(filename)

# callback for received packets
def recv_pkts(hdr, data):
  try:
  	dumper.dump(hdr, data)
  except:
  	exit()

packet_limit = -1 # infinite
pc.loop(packet_limit, recv_pkts) # capture packets