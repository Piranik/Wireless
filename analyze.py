#!/usr/bin/python

#author: Yacked2 on 11.10.2014

#V2: 1.11.2014:
#-shows WPA APs only
#-remove -1 PWR
#-path to rainbow.txt fixed to /usr/bin/rainbow.txt


import sys
import glob
import time
import os
import datetime

#######################################################################
#CONVERTING LIST
#######################################################################
#this function is copied from www, I do not own this part of the source
def PrintTable(table, justify = "C", columnWidth = 0):
    if columnWidth == 0:
        for row in table:
            for col in row:
                width = len(str(col))
                if width > columnWidth:
                    columnWidth = width

    outputStr = ""
    for row in table:
        rowList = []
        for col in row:
            if justify == "R": # justify right
                rowList.append(str(col).rjust(columnWidth))
            elif justify == "L": # justify left
                rowList.append(str(col).ljust(columnWidth))
            elif justify == "C": # justify center
                rowList.append(str(col).center(columnWidth))
        outputStr += ' '.join(rowList) + "\n"

    return outputStr

#######################################################################
#READ DATA FROM .CSV
#######################################################################
def GetData(path):
	#read all data to lines
	f = open(path)
	lines = f.readlines()
	f.close()
	
	#read all table names to tables
	f = open('/usr/bin/rainbow.txt')
	tables = []
	for line in f:
		line = line.replace("\r\n","")
		tables.append(line)
	f.close()
	
	object= []
	zacetekC = -1
	
	for line in lines:
		#if line is not empty
		if(len(line) !=0 and line !="" and line != "\r\n"):
			
			#end of stations, start of clients
			if(line.find("Station MAC, First time seen, Last time seen, Power, # packets, BSSID, Probed ESSIDs") != -1):
				zacetekC = lines.index(line)+1
				break

			#first line
			elif(line.find("BSSID, First time seen, Last time seen, channel, Speed, Privacy, Cipher, Authentication, Power, # beacons, # IV, LAN IP, ID-length, ESSID, Key") != -1):
				pass

			#data line
			else:
				data = []
				line= line.replace("\r\n","")
				part = line.split(", ")
				
				#check if station is still visible (2min from lastseen)
				current = datetime.datetime.now().replace(microsecond=0)
				last = datetime.datetime.strptime(part[2],'%Y-%m-%d %H:%M:%S')
				razlika =current-last
				
				#get data to object
				if(razlika <= datetime.timedelta(minutes=2)):
					#preverimo ali je WPA in ali je PWR manjsi od -1
					if(part[5].find("WPA") != -1 and int(part[7]) < -1):
						
						data.append(part[0])
						data.append(part[12])
						data.append(part[3])
						data.append(part[7])
						object.append(data)
	
	#checking on clients
	withClient = []
	
	#foreach client line
	for i in range (zacetekC,len(lines)-1):
		
		lines[i]= lines[i].replace("\r\n","")
		part = lines[i].split(", ")

		#check if client is still visible
		current = datetime.datetime.now().replace(microsecond=0)
		last = datetime.datetime.strptime(part[2],'%Y-%m-%d %H:%M:%S')
		razlika =current-last

		station = part[5].replace(",","")

		#add to list	
		if(razlika <= datetime.timedelta(minutes=2) and station not in withClient):
			
			withClient.append(station)

	for a in object:
		bssid = a[0] #station MAC
		essid = a[1] #station ESSID
		#do we have a client on AP			
		if(bssid in withClient):
			a.append("YES")
		else:
			a.append("NO")
		
		#do we have table for it
		if essid in tables:
			a.append("YES")
		else:
			a.append("NO")

	return object

#######################################################################
#ORDERING DATA (CLIENT,TABLE,PWR)
#######################################################################
def OrderData(data):
	result = []

	#if we don't have PWR for ap we remove it(to far away)
	for w in data:
		if(w[4] != "" and len(w[4]) !=0 and w[4] != "  "):
			result.append(w)	

	#first sort per PWR (-30 is better than -40)
	result.sort(key=lambda k: (k[3]), reverse=False)

	#sort per table
	result.sort(key=lambda k: (k[5]), reverse=True)

	#sort per client
	result.sort(key=lambda k: (k[4]), reverse=True)

	return result
	
###################################################################
#MAIN APPLICATION
###################################################################

#check on filters
#-c for showing only AP with client
#-t for showing only AP with table

clientOnly = False
tableOnly = False

if(len(sys.argv) ==2 and sys.argv[1]=="-c"):
	clientOnly = True

if(len(sys.argv) ==2 and sys.argv[1]=="-t"):
	tableOnly = True

if(len(sys.argv) ==3 and sys.argv[1]=="-c" and sys.argv[2]=="-t"):
	clientOnly = True
	tableOnly = True

if(len(sys.argv) ==3 and sys.argv[1]=="-t" and sys.argv[2]=="-c"):
	clientOnly = True
	tableOnly = True

#search in root for all .csv files, except .kismet.csv
files = glob.glob("/root/*.csv")

#remove .kismet files
valid = []
for file in files:
	if (file.find(".kismet.csv") == -1):
		valid.append(file)
	
files = valid
path= ""

#no .csv file
if(len(files) ==0):
	print "Please copy .csv file to root"
	sys.exit(0)

#only one, that is our file
elif(len(files) ==1):
	path = files[0]

#more csv files, user choose it
else:
	print ""
	print "Select your file:"
	for file in files:
		print str(files.index(file)) + ": " + file 
	print ""
	path = files[int(raw_input("Select index: "))]
	print ""


while True:
	os.system('clear')	
	data = GetData(path) #read data from .csv file

	data = OrderData(data) #order data

	#if filters are enabled
	#-c filter

	backup = []
	if(clientOnly == True):
		for l in data:
			#print l[5]
			if(l[5] == "YES"):
				backup.append(l)
	else:
		backup = data

	#-t filter
	final = []
	if(tableOnly == True):
		for last in backup:
			if(last[6] == "YES"):
				final.append(last)
	else:
		final = backup
	
	#append headline
	head = [["MAC","ESSID","CHANNEL","PWR","CLIENT","TABLE"]]
	head.extend(final)
	
	#convert list
	head = PrintTable(head)
	print head
	
	#wait 5s and read again
	time.sleep(5)
