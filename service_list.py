import environment as E
import sys

def service_list():
	(list_serv, serv_ip, serv_subn) = E.get_services()
	for s in list_serv:
		if serv_ip.has_key(s):
			print s + " " + serv_ip.get(s) + " " + serv_subn.get(s)
		else: 
			print s


