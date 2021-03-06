#!/home/pi/.virtualenvs/sunlight_rfid_doorman/bin/python

import time
import re
import sys
import itertools

import serial
import envoy

from settings import *
from acl import *

QUIET = '--quiet' in map(lambda x: x.strip(), sys.argv)

def allow(ser, user_id):
	envoy.run('ssh gatekeeper /usr/bin/python /root/cycle.py')
	ser.write('G')				
	if not QUIET:
		print '[PASS] %s | %s' % (datetime.datetime.now().isoformat(), user_id)
	log((time.time(), user_id, 'PASS'))

def deny(ser, rfid_serial):
	ser.write('R')
	if not QUIET:
		print '[DENY] %s | %s' % (datetime.datetime.now().isoformat(), rfid_serial)
	log((time.time(), rfid_serial, 'DENY'))

def main():

	denied_rfid_serials = []

	# refresh the ACL, waiting 5s between attempts
	if not QUIET:
		print 'Retrieving Access Control List...'
	failed = True
	while failed:
		try:
			refresh_access_control_list()
			failed = False
		except:
			failed = True
			time.sleep(5)

	re_identifiers = re.compile(r'\[(.{10})\]')

	# open serial connection (retrying every 5s)
	if not QUIET:
		print 'Opening serial connection...'
	failed = True
	while failed:
		try:
			ser = serial.Serial(SERIAL_PORT, SERIAL_RATE)
			failed = False
		except:
			failed = True
			time.sleep(5)

	if not QUIET:
		print 'Starting...'

	# wait for Arduino to restart due to serial connection
	time.sleep(2) 

	if not QUIET:
		print 'Ready.'
		print ('-' * 60)

	while True:		
		line = ser.readline()		
		acl = get_access_control_list() # refresh from redis

		# pull the RFID serial number from the serial input
		match = re_identifiers.search(line)
		if match is not None:		
			rfid_serial = match.group(1)	
			if rfid_serial in acl.keys():
				allow(ser, acl[rfid_serial])
				denied_rfid_serials = []
			else:
				# is this the first time this serial has failed?
				# if so, check for an updated ACL & rerun check
				if rfid_serial not in denied_rfid_serials:
					ser.write('Y') # signal we're thinking...

					# pull a fresh ACL
					try:
						refresh_access_control_list()
					except:
						pass
					acl = get_access_control_list()
					
					# recheck
					if rfid_serial in acl.keys():
						allow(ser, acl[rfid_serial])
						denied_rfid_serials = []
					else:
						deny(ser, rfid_serial)
						denied_rfid_serials.append(rfid_serial)

				
				else:
					deny(ser, rfid_serial)
					denied_rfid_serials.append(rfid_serial)


if __name__ == '__main__':
	main()
