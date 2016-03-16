import environment as E

def subnet_list():
	neutron = E.get_neutron()
	subnets = neutron.list_subnets()['subnets']
	for s in subnets:
		print s['name'] + " " + s['cidr']	


