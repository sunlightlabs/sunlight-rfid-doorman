#!/home/pi/.virtualenvs/sunlight_rfid_doorman/bin/python

import time
import re
import itertools

import serial
import envoy

from settings import *
from acl import *

def allow(ser, user_id):
	ser.write('G')				
	envoy.run('ssh gatekeeper /usr/bin/python /root/cycle.py')
	print '[PASS] %s | %s' % (datetime.datetime.now().isoformat(), user_id)
	log((time.time(), user_id, 'PASS'))

def deny(ser, rfid_serial):
	ser.write('R')
	print '[DENY] %s | %s' % (datetime.datetime.now().isoformat(), rfid_serial)
	log((time.time(), rfid_serial, 'DENY'))

def main():

	last_rfid_serial = None

	refresh_access_control_list()

	re_identifiers = re.compile(r'\[(.{10})\]')

	print 'Starting...'

	# open serial connection
	ser = serial.Serial(SERIAL_PORT, SERIAL_RATE)

	# wait for Arduino to restart due to serial connection
	time.sleep(2) 

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
			else:
				# is this the first time this serial has failed?
				# if so, check for an updated ACL & rerun check
				if rfid_serial!=last_rfid_serial:
					ser.write('Y') # signal we're thinking...

					# pull a fresh ACL
					refresh_access_control_list()
					acl = get_access_control_list()
					
					# recheck
					if rfid_serial in acl.keys():
						allow(ser, acl[rfid_serial])
					else:
						deny(ser, rfid_serial)

					# record failed serial; we don't want a DOS
					last_rfid_serial = rfid_serial
				
				else:
					deny(ser, rfid_serial)


if __name__ == '__main__':
	main()
