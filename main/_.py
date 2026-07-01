from time import sleep
import logging
import sys

def hold():
	try:
		while True:
			sleep(1)
	except KeyboardInterrupt:
		logging.error('KeyboardInterrupt')
		sys.exit('KeyboardInterrupt')
