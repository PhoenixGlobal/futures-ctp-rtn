from ctpwrapper import ApiStructure
from ctp.trader import BaseTrader

class Trader(BaseTrader):
	# 期货公司响应
	def OnRspOrderInsert(self, pInputOrder, pRspInfo, nRequestID, bIsLast):
		self.log.info('OnRspOrderInsert')
		self.log.info(pInputOrder)
		self.log.info(pRspInfo)
		self.log.info(nRequestID)
		self.log.info(bIsLast)
		pass

	# 订单实时状态推送
	def OnRtnOrder(self, pOrder):
		self.log.info('OnRtnOrder')
		self.log.info(pOrder)

	# 报单插入错误（交易所）
	def OnErrRtnOrderInsert(self, pInputOrder, pRspInfo):
		self.log.error('order insert failed')
		self.log.error(pInputOrder)
		self.log.error(pRspInfo)

	# 成交
	def OnRtnTrade(self, pTrade) -> None:
		self.log.info('OnRtnTrade')
		self.log.info(pTrade)