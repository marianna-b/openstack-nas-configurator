#!/usr/bin/python

import sys

def subnet_list():
	print "subnet list will be here"
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
	sys.exit(1)
