#!/home/pi/.virtualenvs/sunlight_rfid_doorman/bin/python

import time
import re
import itertools

import serial
import gspread
import envoy

from settings import *


last_id_list_update = None

def refresh_access_control_list():	
	gc = gspread.login(USERNAME, PASSWORD)
	sh = gc.open(SPREADSHEET_NAME)	
	worksheet = sh.worksheet(SPREADSHEET_WORKSHEET)
	key_cells = worksheet.col_values(1)
	email_cells = worksheet.col_values(2)
	active_cells = worksheet.col_values(3)
	
	acl = {}

	for (i, (key, email, active)) in enumerate(izip(key_cells, email_cells, active_cells)):
		if i==0:
			continue
		if active.upper().strip()=='Y':
			acl[key.strip()] = email.strip()

	last_id_list_update = time.time()

	return acl

def main():

	acl = refresh_access_control_list()

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
		match = re_identifiers.search(line)
		if match is not None:		
			serial = match.group(1)	
			if match.group(1) in acl.keys():
				ser.write('G')				
				envoy.run('ssh gatekeeper /usr/bin/python /root/cycle.py')
				print '%s (%s) - [OK]' % (serial, acl[serial])
			else:
				print '%s - [DENY]' % (serial)
				ser.write('R')


if __name__ == '__main__':
	main()
