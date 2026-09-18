from fommon.app_config.read import app_config
from fommon import log
from ._trader import Trader

ctp_trader = Trader()

def init():
	log.inf('initing ctp trader')
	ctp_trader.Create()
	server = app_config['ctp']['trade_server']
	ctp_trader.RegisterFront(f'tcp://{server['ip']}:{server['port']}')
	ctp_trader.SubscribePrivateTopic(
		1, # 从上次断开后接收
		8888, # SubscribePrivateTopic 未用到这个参数，我瞎写的
	)
	ctp_trader.Init()

	log.inf(f'ctp trader initialized, trading day: {ctp_trader.GetTradingDay()}')

def clear():
	ctp_trader.Release()
