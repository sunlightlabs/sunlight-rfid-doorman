import time
import re

import serial
import gspread

from settings import *


def approved_id_list():
	for x in ['74E81E0587']:
		yield x

def main():

	re_identifiers = re.compile(r'\[([0-9A-F])\]')

	# open serial connection
	ser = serial.Serial(SERIAL_PORT, SERIAL_RATE)

	# wait for Arduino to restart due to serial connection
	time.sleep(2) 

	while line = ser.readline():
		match = re_identifiers.search(line)
		if match is not None:
			if match.group(1) in approved_id_list():
				ser.write('G')
			else:
				ser.write('R')


if __name__ == '__main__':
	main()