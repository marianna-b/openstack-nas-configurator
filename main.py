#!/usr/bin/python

import sys

#TODO move to config separate file
from neutronclient.v2_0 import client
from netaddr import *
username = 'admin'
password = 'secret'
tenant_name = 'demo'
auth_url = 'http://10.64.77.53:35357/v2.0'
neutron = client.Client(username = username, 
			password = password, 
			tenant_name = tenant_name,
			auth_url = auth_url)
try:
	f = open('services.cfg', 'r')
except:
	print "No services.cfg file found"
	sys.exit(1)
serv_cfg = f.readlines()
try:
	list_serv = serv_cfg[0].split()

	serv_ip = {}
	for i in range (1, len(serv_cfg)):
		cur = serv_cfg[i].split();
		serv_ip[cur[0]] = cur[1]
except:
	print "Wrong config file format"

def subnet_list():

	subnets = neutron.list_subnets()['subnets']
	for s in subnets:
		print s['name'] + " " + s['cidr']	

def service_list():
	for s in list_serv:
		if serv_ip.has_key(s):
			print s + " " + serv_ip.get(s)
		else: 
			print s

def check(ip, subn):
	pools = subn['allocation_pools']	
	ipset = IPSet()
	for p in pools:
		ipset.add(IPRange(p['start'], p['end']))
	if not(ip in ipset):
		return False

	ports = neutron.list_ports()['ports']
	for p in ports:
		for i in p['fixed_ips']:
			if i['subnet_id'] == subn['id']:
				if ip == i['ip_address']:
					return False
	return True

def alloc_ip(subn):
	pools = subn['allocation_pools']	
	ans = ""	
	for p in pools:
		range = IPRange(p['start'], p['end'])
		for ip in range:
			if check(ip, subn):
				ans = ip
	reserv_ip(ans, subn)	

def reserv_ip(ip, subn):
	pools = subn['allocation_pools']	
	new_pools = []
	ip_addr = IPAddress(ip)
	for p in pools:
		if ip in IPRange(p['start'], p['end']):
			if p['start'] == p['end']:
				continue
			if ip != p['end']:
				new_pools.append(
						{'start': str(ip_addr + 1),
					 	 'end' : p['end'] })	
			if ip != p['start']:
				new_pools.append(
						{'start': p['start'],
						 'end' :  str(ip_addr - 1)})	
		else:
			new_pools.append(p)
	
	subn2 = {'allocation_pools' : new_pools }
	try:
		neutron.update_subnet(subn['id'], {'subnet' : subn2})
	except Exception, e:
		print str(e)

def join():
	if len(sys.argv) < 4:
		print "Not enough arguments for join" #TODO add help
		return
	subn = sys.argv[2]
	serv = sys.argv[3]
	res = True
	cur_ip = ""
	subnet = neutron.list_subnets(name=subn)['subnets'][0]
	if serv_ip.has_key(serv):
		try:
			cur_ip = serv_ip.get(serv)
			res = check(cur_ip, subnet)
			if res:
				reserv_ip(cur_ip, subnet)
		except:
			print "Unknown subnet"
			return		
	else:
		cur_ip = alloc_ip(subnet)
	if not res:
		print "Failed to start server: bad ip address"
		#TODO
		return		


parse = {"subnet-list" : subnet_list,
	 "service-list" : service_list,
	 "join" : join,
}
if len(sys.argv) < 2:
	print "Not enough arguments" #TODO add help
	sys.exit(1)
try:
	parse[sys.argv[1]]()
except:
	print "No such option: " + sys.argv[1] 
	print "Available options: subnet-list, service-list, join <subnet> <service>"
	sys.exit(1)


