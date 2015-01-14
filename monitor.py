#!/usr/bin/python

import sys
import os
import subprocess

interfaces = [];

output = subprocess.check_output(["airmon-ng"])

lines = output.splitlines()

for line in lines:
	if(len(line) != 0 and line != "" and line.find("Interface") == -1):
		face=""
		for char in line:
			if(char != " " and char != "\t"):
				face = face + char
			else:
				interfaces.append(face)
				break

interface = ""
if(len(interfaces) > 1):
	print "Choose index of your device:"
	for face in interfaces:
		print str(interfaces.index(face)) + ": " +face

	print ""
	index = raw_input("Selected index: ")
	print ""
	index = int(index)
	if(index < len(interfaces)):
		interface = interfaces[index]
	else:
		print "Out of array"
		sys.exit(0)

elif(len(interfaces) == 1):
	interface = interfaces[0]
else:
	print "Cannot find your device!"
	sys.exit(0)

os.system("ifconfig " + interface + " down")
os.system("ifconfig " + interface + " hw ether 00:11:00:11:00:11")
os.system("ifconfig " + interface + " up")

output = subprocess.check_output(["airmon-ng","start",interface])

zacetek = output.index("monitor mode enabled on ")+24

monitor = ""

for char in range(zacetek, len(output)):
	if(output[char] != ")"):
		monitor = monitor + output[char]
	else:
		break


os.system("ifconfig " + monitor + " down")
os.system("macchanger -m 00:11:00:11:00:11 " + monitor + " > /dev/null")
os.system("ifconfig " + monitor + " up")

output = subprocess.check_output(["airmon-ng","check",monitor])

if(output != 0 and output != "" and output != " "):
	zacetek = -1
	lines = output.splitlines()
	
	for line in lines:
		if(line.find("PID") != -1):
			zacetek = lines.index(line) +1

	for i in range(zacetek,len(lines)):
		#print lines[i].split()[0]
		os.system("kill " + lines[i].split()[0])

	
print "Your device: " + interface
print "Monitor mode enabled on: " + monitor
print "Your new MAC: 00:11:00:11:00:11"

