# Wireless
Script created to analyze wireless networks:
  direct.py: 
  Is used to attack WPA encrypted networks with no client, so we won't gain no handshake. This method is very slow.
  
  monitor.py:
  Start our wifi interface and change its MAC address.
  
  analyze.py:
  First start airodump-ng with capturing to a file, this script will read from this file and show us data in more efficient way. Can add "-c" arg to show only APs with client or "-t" to show only APs with rainbow table avaible.
