import sys
from neutronclient.v2_0 import client

def get_neutron():
	username = 'admin'
	password = 'secret'
	tenant_name = 'demo'
	auth_url = 'http://10.64.77.53:35357/v2.0'
	neutron = client.Client(username = username, 
			password = password, 
			tenant_name = tenant_name,
			auth_url = auth_url)
	return neutron

def get_services():
	try:
		f = open('services.cfg', 'ra')
	except:
		print "No services.cfg file found"
		sys.exit(1)
	serv_cfg = f.readlines()
	f.close()
	try:
		list_serv = serv_cfg[0].split()
		serv_ip = {}
		serv_subn = {}
		for i in range (1, len(serv_cfg)):
			cur = serv_cfg[i].split();
			serv_ip[cur[0]] = cur[1]
			serv_subn[cur[0]] = cur[2]
	except:
		print "Wrong config file format"
	return (list_serv, serv_ip, serv_subn)

def get_server():
	try:
		f = open('server.cfg', 'ra')
	except:
		print "No server.cfg file found"
		sys.exit(1)
	serv_cfg = f.readlines()
	f.close()
	return (serv_cfg[0], serv_cfg[1])
