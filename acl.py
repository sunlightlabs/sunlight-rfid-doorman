#!/home/pi/.virtualenvs/sunlight_rfid_doorman/bin/python

import pickle
import datetime
import time
import itertools

import redis
import gspread

from settings import *

ACL_KEY = 'sunlight-doorman-acl'
LOG_KEY = 'sunlight-doorman-log'

def refresh_access_control_list(gc=None):	
	if gc is None:
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

	r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=0)
	r.set(ACL_KEY, pickle.dumps(acl))


def get_access_control_list():
	r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=0)
	if not r.exists(ACL_KEY):
		return False
	else:
		return pickle.loads(r.get(ACL_KEY))

def log(status):
	r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=0)
	r.rpush(LOG_KEY, pickle.dumps(status))

def _log_worksheet_name(timestamp):
	dt = datetime.datetime.fromtimestamp(float(timestamp))
	return 'log - %d/%d' % (dt.month, dt.year)
	

def store_log(gc=None):
	if gc is None:
		gc = gspread.login(SPREADSHEET_USER, SPREADSHEET_PASSWORD)

	# open spreadsheet
	ss = gc.open(SPREADSHEET_NAME)

	# load log entries out of redis
	log_items = []
	r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=0)
	while True:
		log_item = r.lpop(LOG_KEY)
		if log_item is None:
			break
		log_items.append(pickle.loads(log_item))

	# assemble data by month
	log_worksheets = {}
	for l in log_items:
		timestamp = l[0]
		worksheet_name = _log_worksheet_name(timestamp)
		if not log_worksheets.has_key(worksheet_name):
			log_worksheets[worksheet_name] = {'log_items': []}
		log_worksheets[worksheet_name]['log_items'].append(l)

	# store log entries
	for lw in log_worksheets:
		
		# create monthly worksheets as necessary
		try:
			ws = ss.worksheet(lw)
			ws_offset = len(ws.col_values(1)) + 1
		except:
			ws = ss.add_worksheet(title=lw, rows="10000", cols="3")
			ws_offset = 1

		# store log items
		cell_list = ws.range('A%(begin)d:C%(end)d' % {'begin': ws_offset, 'end': ws_offset + len(log_worksheets[lw]['log_items']) - 1})
		for (i, log_item) in enumerate(log_worksheets[lw]['log_items']):
			cell_list[(3*i) + 0].value = datetime.datetime.fromtimestamp(float(log_item[0])).isoformat()
			cell_list[(3*i) + 1].value = log_item[1]
			cell_list[(3*i) + 2].value = log_item[2]
		ws.update_cells(cell_list)


if __name__ == '__main__':
	gc = gspread.login(SPREADSHEET_USER, SPREADSHEET_PASSWORD)
	refresh_access_control_list(gc)
	store_log(gc)
