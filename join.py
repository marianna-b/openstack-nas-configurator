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

def ssh_add_device(s, vlan_id, nmsp, cur_ip, serv):	
	s.sendline("sudo ./add_serv.sh " + serv + " " + nmsp + " " + vlan_id + " " + cur_ip)


def login(ip, s):
	username = raw_input("user: ")
	password = getpass.getpass("pswd: ")
	s.login(ip, username, password)
	

def init_service(serv, cur_ip, vlan_id, list_serv, serv_ip):
	servIPList = ""
	for n in serv_ip:
		servIPList += n + ' ' + serv_ip[n] + ' ';
	nmsp = "ns" + serv[1:]
	(ip, path) = E.get_server()	
	path = path[:-1]
	s = pxssh.pxssh()
	login(ip, s)
	print path
	print servIPList 
	s.sendline("cd " + path + "nas-srv-et-scripts")
	s.sendline("sudo ./delete_services")
	s.sendline("./gen_cfg.sh " + servIPList)
	ssh_add_device(s, str(vlan_id), nmsp, cur_ip, serv)	
	s.sendline("sudo ./install_server")
	s.sendline("cd " + path + "nas-srv-et-app")
	s.sendline("sudo ./restart_server")
	s.logout()

def add_device(serv, cur_ip, vlan_id, list_serv, serv_ip):
	s = pxssh.pxssh()
	(ip, path) = E.get_server()	
	login(ip, s)
	nmsp = "ns" + serv[1:]
	ssh_add_device(s, str(vlan_id), nmsp, cur_ip, serv)	
	s.logout()

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

			f.write(serv + " " + cur_ip + '\n')
			f.close()
		except Exception, e:
			print str(e)
	if not res:
		print "Failed to start server: bad ip address"
		#return		
	vlan_id = neutron.list_networks(id = subnet['network_id'])['networks'][0]['provider:segmentation_id']
	if serv_ip.has_key(serv):
		add_device(serv, cur_ip, vlan_id, list_serv, serv_ip)	
	else:
		serv_ip[serv]=cur_ip
		init_service(serv, cur_ip, vlan_id, list_serv, serv_ip)

