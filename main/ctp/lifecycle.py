from lib.fommon.singleton import Singleton
from lib.fommon.app_config.read import app_config
from lib.fommon import log
from .trader import Trader

class Lifecycle(Singleton[Trader]):
	def _create(self):
		log.inf('initing ctp trader')
		server = app_config['ctp']['trade_server']
		trader = Trader()
		trader.Create()
		trader.RegisterFront(f'tcp://{server['ip']}:{server['port']}')
		trader.SubscribePrivateTopic(
			1, # 从上次断开后发
			8888, # SubscribePrivateTopic 未用到这个参数，我瞎写的
		)
		trader.Init()

		log.inf(f'ctp trader initialized, trading day: {trader.GetTradingDay()}')
		return trader

	def _destroy(self, instance):
		instance.Release()
