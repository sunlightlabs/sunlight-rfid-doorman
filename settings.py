SERIAL_PORT = '/dev/ttyACM0'
SERIAL_RATE = 115200

SPREADSHEET_NAME = 'Sunlight Door Access'
SPREADSHEET_WORKSHEET = 'ACL'
SPREADSHEET_USER = 'judgebrandeis@sunlightfoundation.com'
SPREADSHEET_PASSWORD = 'set this in local_settings.py'

REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379

try:
	from local_settings import *
except:
	pass