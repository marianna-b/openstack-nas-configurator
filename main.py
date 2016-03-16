#!/usr/bin/python

import subnet_list as SL1
import service_list as SL2
import join as J
from netaddr import *
import sys

def subnet_list_wrap():
	SL1.subnet_list()	

def service_list_wrap():
	SL2.service_list()

def join_wrap():
	if len(sys.argv) < 4:
		print "Not enough arguments for join" #TODO add help
		return
	subn = sys.argv[2]
	serv = sys.argv[3]

	J.join(subn, serv)

parse = {"subnet-list" : subnet_list_wrap,
	 "service-list" : service_list_wrap,
	 "join" : join_wrap,
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


