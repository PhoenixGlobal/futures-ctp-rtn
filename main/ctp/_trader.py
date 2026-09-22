import time
from typing import Self
from ctpwrapper import ApiStructure
from ctp.trader import BaseTrader
from fommon.app_config.read import app_config
from fommon import log
from . import util as _

class Trader(BaseTrader):
	def __init__(self):
		def after_login(self: Self):
			self.daily_job()
			self.__last_daily_job = self.GetTradingDay()
		self.__last_daily_job = ''
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

	def daily_job(self):
		''' 
		每日任务:
		1. 确认结算单
		2. 查询账户
		3. 查询仓位
		'''

		log.inf('开始日常任务')
		self.__confirm_settlement()

	def __confirm_settlement(self):
		log.inf('confirming settlement')
		settlement = ApiStructure.SettlementInfoConfirmField(
			BrokerID = app_config['ctp']['broker'],
			InvestorID = app_config['ctp']['investor'],
		)
		ret = self.ReqSettlementInfoConfirm(settlement, self.req_id())
		assert ret == 0, f'确认结算单失败: {ret}'
	# 确认结算单
	def OnRspSettlementInfoConfirm(self, pSettlementInfoConfirm, pRspInfo, nRequestID, bIsLast):
		_.save('RspSettlementInfoConfirm', pSettlementInfoConfirm, pRspInfo, nRequestID, bIsLast)
		self.__query_account()

	def __query_account(self):
		log.inf('querying account')
		input = ApiStructure.QryTradingAccountField(
			BrokerID = app_config['ctp']['broker'],
			InvestorID = app_config['ctp']['investor'],
			BizType = '1',
		)
		ret = self.ReqQryTradingAccount(input, self.req_id())
		assert ret == 0, f'查询账户失败: {ret}'
	# 查询账户（余额等）
	def OnRspQryTradingAccount(self, pTradingAccount, pRspInfo, nRequestID, bIsLast):
		_.save('RspQryTradingAccount', pTradingAccount, pRspInfo, nRequestID, bIsLast)
		self.__query_position()

	def __query_position(self):
		log.inf('querying position')
		position = ApiStructure.QryInvestorPositionField(
			BrokerID = app_config['ctp']['broker'],
			InvestorID = app_config['ctp']['investor'],
		)
		ret = self.ReqQryInvestorPosition(position, self.req_id())
		assert ret == 0, f'查询仓位失败: {ret}'
	# 查询仓位
	def OnRspQryInvestorPosition(self, pInvestorPosition, pRspInfo, nRequestID, bIsLast):
		_.save('RspQryInvestorPosition', pInvestorPosition, pRspInfo, nRequestID, bIsLast)

	def place_order(self, order: ApiStructure.InputOrderField):
		trading_day = self.GetTradingDay()
		if self.__last_daily_job != trading_day:
			log.inf('日常任务已过期')
			self.daily_job()
			time.sleep(.1)
			self.__last_daily_job = trading_day

		ret = self.ReqOrderInsert(order, order.RequestID)
		assert ret == 0, f'下单失败: {ret}'
