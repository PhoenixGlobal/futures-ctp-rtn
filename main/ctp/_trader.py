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
		1. 查询账户
		2. 查询仓位
		'''

		log.inf('开始日常任务')
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
		self.query_position()

	def query_position(self) -> int:
		self.wait_ready_to_trade()
		log.inf(f'查询仓位...')
		position = ApiStructure.QryInvestorPositionField(
			BrokerID = app_config['ctp']['broker'],
			InvestorID = app_config['ctp']['investor'],
		)
		rid = self.req_id()
		ret = self.ReqQryInvestorPosition(position, rid)
		assert ret == 0, f'查询仓位失败: {ret}'
		return rid
	# 查询仓位
	def OnRspQryInvestorPosition(self, pInvestorPosition, pRspInfo, nRequestID, bIsLast):
		_.save('RspQryInvestorPosition', pInvestorPosition, pRspInfo, nRequestID, bIsLast)

	def place_order(self, order: ApiStructure.InputOrderField):
		self.wait_ready_to_trade()
		trading_day = self.GetTradingDay()
		if self.__last_daily_job != trading_day:
			log.inf('日常任务已过期')
			self.daily_job()
			time.sleep(.1)
			self.__last_daily_job = trading_day

		ret = self.ReqOrderInsert(order, order.RequestID)
		assert ret == 0, f'下单失败: {ret}'
