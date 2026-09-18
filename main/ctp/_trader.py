from typing import Self
from ctpwrapper import ApiStructure
from ctp.trader import BaseTrader
from fommon.app_config.read import app_config
from fommon import log
from . import _util as _

class Trader(BaseTrader):
	def __init__(self):
		def after_login(self: Self):
			self.daily_job()
		super().__init__(after_login)

	# 报单
	def OnRtnOrder(self, pOrder):
		_.save('RtnOrder', pOrder)
		log.inf(
			f'order: {pOrder.OrderRef}; '
			f'volume: {pOrder.VolumeTotalOriginal}; '
			f'已成交: {pOrder.VolumeTraded}; '
			f'未成交: {pOrder.VolumeTotal}; '
			f'status: {pOrder.OrderStatus}.'
		)
	# 成交
	def OnRtnTrade(self, pTrade) -> None:
		_.save('RtnTrade', pTrade)
		log.inf(
			f'order {pTrade.OrderRef}; '
			f'volume: {pTrade.Volume};'
			f'price: {pTrade.Price}'
		)

	# 报单 (期货公司)
	def OnRspOrderInsert(self, pInputOrder, pRspInfo, nRequestID, bIsLast):
		_.save('RspOrderInsert', pInputOrder, pRspInfo, nRequestID, bIsLast)
	# 报单错误 (交易所)
	def OnErrRtnOrderInsert(self, pInputOrder, pRspInfo):
		_.save('ErrRtnOrderInsert', pInputOrder, pRspInfo)

	# 确认结算单
	def OnRspSettlementInfoConfirm(self, pSettlementInfoConfirm, pRspInfo, nRequestID, bIsLast):
		_.save('RspSettlementInfoConfirm', pSettlementInfoConfirm, pRspInfo, nRequestID, bIsLast)

	# 查询仓位
	def OnRspQryInvestorPosition(self, pInvestorPosition, pRspInfo, nRequestID, bIsLast):
		_.save('RspQryInvestorPosition', pInvestorPosition, pRspInfo, nRequestID, bIsLast)

	# 查询账户（余额等）
	def OnRspQryTradingAccount(self, pTradingAccount, pRspInfo, nRequestID, bIsLast):
		_.save('RspQryTradingAccount', pTradingAccount, pRspInfo, nRequestID, bIsLast)

	def daily_job(self):
		''' 
		每日任务:
		1. 确认结算单
		2. 查询账户
		3. 查询仓位
		'''

		log.inf('confirming settlement')
		settlement = ApiStructure.SettlementInfoConfirmField(
			BrokerID = app_config['ctp']['broker'],
			InvestorID = app_config['ctp']['investor'],
		)
		ret = self.ReqSettlementInfoConfirm(settlement, self.req_id())
		assert ret == 0, f'确认结算单失败: {ret}'

		log.inf('querying account')
		input = ApiStructure.QryTradingAccountField(
			BrokerID = app_config['ctp']['broker'],
			InvestorID = app_config['ctp']['investor'],
			BizType = '1',
		)
		ret = self.ReqQryTradingAccount(input, self.req_id())
		assert ret == 0, f'查询账户失败: {ret}'

		log.inf('querying position')
		position = ApiStructure.QryInvestorPositionField(
			BrokerID = app_config['ctp']['broker'],
			InvestorID = app_config['ctp']['investor'],
		)
		ret = self.ReqQryInvestorPosition(position, self.req_id())
		assert ret == 0, f'查询仓位失败: {ret}'

	def place_order(self, order: ApiStructure.InputOrderField):
		ret = self.ReqOrderInsert(order, order.RequestID)
		assert ret == 0, f'下单失败: {ret}'
