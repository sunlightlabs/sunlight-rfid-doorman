#!/home/pi/.virtualenvs/sunlight_rfid_doorman/bin/python

import itertools

import redis
import gspread

from settings import *

ACL_KEY = 'sunlight-doorman-acl'

def refresh_access_control_list():	
	gc = gspread.login(SPREADSHEET_USER, SPREADSHEET_PASSWORD)
	sh = gc.open(SPREADSHEET_NAME)	
	worksheet = sh.worksheet(SPREADSHEET_WORKSHEET)
	key_cells = worksheet.col_values(1)
	email_cells = worksheet.col_values(2)
	active_cells = worksheet.col_values(3)
	
	acl = {}

	for (i, (key, email, active)) in enumerate(itertools.izip(key_cells, email_cells, active_cells)):
		if i==0:
			continue
		if active.upper().strip()=='Y':
			acl[key.strip()] = email.strip()

	r = redis.StrictRedis(host='127.0.0.1', port=6379, db=0)
	r.set(ACL_KEY, acl)


def get_access_control_list():
	r = redis.StrictRedis(host='127.0.0.1', port=6379, db=0)
	if not r.exists(ACL_KEY):
		return False
	else:
		return r.get(ACL_KEY)

if __name__ == '__main__':
	refresh_access_control_list()