from ctpwrapper import ApiStructure
from ctp.trader import BaseTrader
import util
from .db import db

class Trader(BaseTrader):
	# 期货公司响应
	def OnRspOrderInsert(self, pInputOrder, pRspInfo, nRequestID, bIsLast):
		self.log.info('OnRspOrderInsert')
		self.log.info(nRequestID)

	# 订单实时状态推送
	def OnRtnOrder(self, pOrder: ApiStructure.OrderField):
		self.log.info(f'OnRtnOrder (req_id: {pOrder.RequestID})')
		db['RtnOrder'].insert_one({
			'data': pOrder.to_dict(),
			'timestamp': util.now(),
		})
		self.log.info(f'RtnOrder (req_id: {pOrder.RequestID}) saved')

	# 报单插入错误（交易所）
	def OnErrRtnOrderInsert(self, pInputOrder, pRspInfo):
		self.log.error('order insert failed')
		self.log.error(pInputOrder)
		self.log.error(pRspInfo)

	# 成交
	def OnRtnTrade(self, pTrade) -> None:
		self.log.info('OnRtnTrade')
		self.log.info(pTrade)