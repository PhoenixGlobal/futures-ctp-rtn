from time import sleep
import logging
import socket
from contextlib import closing
import _env as env
import sys
from trader import Trader

logging.basicConfig(level=logging.INFO)

def check_address_port():
	with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
		if sock.connect_ex(env.trader_server) == 0:
			return True
		else:
			return False

def main():
	logging.info('STARTING futures-ctp-rtn')
	if check_address_port() == False:
		logging.error('trader server down')
		return

	user_trader = Trader(1)
	user_trader.Create()
	ip, port = env.trader_server
	user_trader.RegisterFront(f'tcp://{ip}:{port}')
	user_trader.SubscribePrivateTopic(
		1, # 从上次断开后发
		8888, # SubscribePrivateTopic 未用到这个参数，我瞎写的
	)
	user_trader.Init()

	logging.info('trader api started')
	logging.info(f'trading day: {user_trader.GetTradingDay()}')

	if user_trader.login:
		logging.info('futures-ctp-rtn ONLINE')
		hold()
	else:
		logging.error('futures-ctp-rtn OFFLINE')

def hold():
	try:
		while True:
			sleep(1)
	except KeyboardInterrupt:
		logging.error('KeyboardInterrupt')
		sys.exit('KeyboardInterrupt')

main()
