from ctpwrapper import ApiStructure
from ctp.trader import BaseTrader
from lib.fommon.app_config.read import app_config
from .. import misc
from . import util as _

def after_login(trader: BaseTrader):
	trader.log.info('ctp trader logged in')
	settlement = ApiStructure.SettlementInfoConfirmField(
		BrokerID = app_config['ctp']['broker'],
		InvestorID = app_config['ctp']['investor'],
	)
	trader.log.info('confirming settlement')
	trader.ReqSettlementInfoConfirm(settlement, trader.req_id())

class Trader(BaseTrader):
	def __init__(self):
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
