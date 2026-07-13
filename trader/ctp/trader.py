import env
from ctp.trader import BaseTrader
from trader import misc
from . import util as _

class Trader(BaseTrader):
	def __init__(self):
		def after_login(_):
			misc.log.info('ctp trader logged in')
		super().__init__(after_login, misc.log_name)

	# 报单
	def OnRtnOrder(self, pOrder):
		_.save('RtnOrder', pOrder)
		self.log.info(
			f'order: {pOrder.OrderRef}; '
			f'volume: {pOrder.VolumeTotalOriginal}; '
			f'已成交: {pOrder.VolumeTraded}; '
			f'未成交: {pOrder.VolumeTotal}; '
			f'status: {pOrder.OrderStatus}.'
		)
	# 成交
	def OnRtnTrade(self, pTrade) -> None:
		_.save('RtnTrade', pTrade)
		self.log.info(
			f'order {pTrade.OrderRef}; '
			f'volume: {pTrade.Volume};'
			f'price: {pTrade.Price}'
		)

	# 报单 (期货公司)
	def OnRspOrderInsert(self, pInputOrder, pRspInfo, nRequestID, bIsLast):
		_.save('RspOrderInsert', pInputOrder, pRspInfo, nRequestID, bIsLast)
	# 报单错误 (交易所)
	def OnErrRtnOrderInsert(self, input, pRspInfo):
		_.save('ErrRtnOrderInsert', input, pRspInfo)

	# 确认结算单
	def OnRspSettlementInfoConfirm(self, result, pRspInfo, nRequestID, bIsLast):
		_.save('RspSettlementInfoConfirm', result, pRspInfo, nRequestID, bIsLast)

def init_trader():
	misc.log.info('initing ctp trader')
	trader = Trader()
	trader.Create()
	ip, port = env.trader_server
	trader.RegisterFront(f'tcp://{ip}:{port}')
	trader.SubscribePrivateTopic(
		1, # 从上次断开后发
		8888, # SubscribePrivateTopic 未用到这个参数，我瞎写的
	)
	trader.Init()

	misc.log.info(f'ctp trader initialized, trading day: {trader.GetTradingDay()}')
	return trader
