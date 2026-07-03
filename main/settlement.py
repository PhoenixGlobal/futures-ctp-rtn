import logging
from ctp.trader import BaseTrader
from ctpwrapper import ApiStructure
import env
from . import _

class SettlementTrader(BaseTrader):
	def OnRspSettlementInfoConfirm(self, pSettlementInfoConfirm, pRspInfo, nRequestID, bIsLast):
		logging.info(f'“确认结算”响应:')
		logging.info(pSettlementInfoConfirm)
		logging.info(pRspInfo)
	def OnRspQrySettlementInfo(self, pSettlementInfo, pRspInfo, nRequestID, bIsLast):
		logging.info(f'settlement info:')
		logging.info(pSettlementInfo)
		logging.info(pRspInfo)
	def OnRspQrySettlementInfoConfirm(self, pSettlementInfoConfirm, pRspInfo, nRequestID, bIsLast):
		logging.info(f'settlement confirm info:')
		logging.info(pSettlementInfoConfirm)
		logging.info(pRspInfo)

def on_login(trader: SettlementTrader):
	logging.info('futures-trader ONLINE')

	settlement = ApiStructure.SettlementInfoConfirmField(
		BrokerID = env.broker,
		InvestorID = env.investor,
	)
	logging.info('confirming settlement')
	ret = trader.ReqSettlementInfoConfirm(settlement, trader.req_id())
	logging.error(f'settlement ret: {ret}')

_.main(SettlementTrader, on_login, True)
