#!/usr/bin/python

import sys

#TODO move to config separate file
from neutronclient.v2_0 import client
username = 'admin'
password = 'secret'
tenant_name = 'demo'
auth_url = 'http://10.64.77.53:35357/v2.0'
neutron = client.Client(username = username, 
			password = password, 
			tenant_name = tenant_name,
			auth_url = auth_url)


print neutron
def subnet_list():
	subnets = neutron.list_subnets()['subnets']
	for s in subnets:
		print s['name'] + " " + s['cidr']	

def service_list():
	print "service list will be here"

def join():
	if len(sys.argv) < 4:
		print "Not enough arguments for join" #TODO add help
		return
	print "we will join " + sys.argv[2] + " with " + sys.argv[3]

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


