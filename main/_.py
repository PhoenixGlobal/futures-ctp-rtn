from time import sleep
from typing import Callable
import logging
import sys
from ctp.trader import BaseTrader
import env

def hold():
	try:
		while True:
			sleep(60)
	except KeyboardInterrupt:
		logging.error('KeyboardInterrupt')
		sys.exit('KeyboardInterrupt')

def main(Trader: BaseTrader, on_login: Callable[[BaseTrader], None], _hold: bool):
	logging.basicConfig(level=logging.INFO)
	trader = Trader(on_login)
	trader.Create()
	ip, port = env.trader_server
	logging.info(f'registering front: {ip}:{port}')
	trader.RegisterFront(f'tcp://{ip}:{port}')
	trader.SubscribePrivateTopic(
		1, # 从上次断开后发
		8888, # SubscribePrivateTopic 未用到这个参数，我瞎写的
	)
	trader.Init()
	logging.info(f'trading day: {trader.GetTradingDay()}')
	if _hold:
		hold()