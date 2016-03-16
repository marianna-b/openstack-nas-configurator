import environment as E
from netaddr import *
from neutronclient.v2_0 import client
import pxssh
import getpass

def check(ip, subn, neutron):
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

def reserv_ip(ip, subn, neutron):
	pools = subn['allocation_pools']	
	new_pools = []
	print ip
	ip_addr = IPAddress(ip)
	for p in pools:
		if ip_addr in IPRange(p['start'], p['end']):
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

def alloc_ip(subn, neutron):
	pools = subn['allocation_pools']	
	ans = ""	
	for p in pools:
		range = IPRange(p['start'], p['end'])
		for ip in range:
			if check(ip, subn, neutron):
				reserv_ip(str(ip), subn, neutron)	
				return str(ip)

def init_server(serv, cur_ip, vlan_id, list_serv, serv_ip):
	servList = ""
	for i in list_serv:
		if serv_ip.has_key(i):
			if servList != "":
				servList += ","
			servList += '"' + i +'"'	
	servIPList = ""
	for n in serv_ip:
		servIPList += n +': { service_Ip = ["' + serv_ip[n] + '"]; }; ';
		servIPList += "\n"
	(ip, path, cfg) = E.get_server()	
	s = pxssh.pxssh()
	s.login(ip, 'c4dev', 'c4dev!')
	s.sendline("cd " + path)
	conf = 'echo \'application: {' + "\n" + 'connectSocket: ' + cfg + "\n"
	conf += "services: {\n " + 'serviceNamesList = ('  + servList +');';
	conf += "\n" + servIPList + "\n };\n}"
	conf += '\' > server_config.cfg';
	s.sendline(conf)
	s.prompt()



def join(subn, serv):
	neutron = E.get_neutron()
	(list_serv, serv_ip) = E.get_services()
	res = True
	cur_ip = ""
	subnet = neutron.list_subnets(name = subn)['subnets'][0]
	if serv_ip.has_key(serv):
		try:
			cur_ip = serv_ip.get(serv)
			res = check(cur_ip, subnet, neutron)
			if res:
				reserv_ip(cur_ip, subnet, neutron)
		except:
			print "Unknown subnet"
			return		
	else:
		cur_ip = alloc_ip(subnet, neutron)
		try:
			f = open('services.cfg', 'a')
			f.write(serv + " " + cur_ip)
			f.close()
		except Exception, e:
			print str(e)
	if not res:
		print "Failed to start server: bad ip address"
		#TODO
		#return		
	vlan_id = neutron.list_networks(id = subnet['network_id'])['networks'][0]['provider:segmentation_id']
	init_server(serv, cur_ip, vlan_id, list_serv, serv_ip)


