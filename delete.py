import environment as E
from netaddr import *
from neutronclient.v2_0 import client
import pxssh
import getpass

def return_ip(ip, subn, neutron):
	pools = subn['allocation_pools']	
	pools.append( {'start': ip, 'end' : ip})
	subn2 = {'allocation_pools' : pools }
	try:
		neutron.update_subnet(subn['id'], {'subnet' : subn2})
	except Exception, e:
		print str(e)

def login(ip, s):
	username = raw_input("user: ")
	password = getpass.getpass("pswd: ")
	s.login(ip, username, password)
	

def delete_service(serv, serv_ip):
	servIPList = ""
	for n in serv_ip:
		servIPList += n + ' ' + serv_ip[n] + ' ';
	nmsp = "ns" + serv[1:]
	(ip, path) = E.get_server()	
	path = path[:-1]
	s = pxssh.pxssh()
	login(ip, s)
	print servIPList 
	s.sendline("cd " + path + "nas-srv-et-scripts")
	s.sendline("./gen_cfg.sh " + servIPList)

	s.sendline("sudo ./del_serv.sh " + serv + " " + nmsp )

	s.sendline("sudo ./install_server")
	s.sendline("cd " + path + "nas-srv-et-app")
	s.sendline("sudo ./restart_server")
	s.logout()

def delete(serv):
	neutron = E.get_neutron()
	(list_serv, serv_ip, serv_subn) = E.get_services()
	if not serv_ip.has_key(serv):
		print "Failed to delete: service is not in use"
		return		
	ip = serv_ip[serv]
	subn = serv_subn[serv]
	serv_ip.pop(serv)
	serv_subn.pop(serv)

	subnet = neutron.list_subnets(name = subn)['subnets'][0]
	return_ip(ip, subnet, neutron)
	delete_service(serv, serv_ip)

	try:
		f = open('services.cfg', 'w')
		for s in list_serv:
			f.write(s + ' ')
		f.write('\n')
		for n in serv_ip:
			f.write(n + ' ' + serv_ip[n]+ ' ' + serv_subn[n] + '\n')
		f.close()
	except Exception, e:
		print str(e)
