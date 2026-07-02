import logging
from datetime import datetime
from ctp.trader import BaseTrader
from ctpwrapper import ApiStructure
import env
from . import _

class QPTrader(BaseTrader):
	def OnRspQryInvestorPosition(self, pInvestorPosition, pRspInfo, nRequestID, bIsLast):
		logging.info('当前仓位')
		logging.info(pInvestorPosition)
		logging.info(pRspInfo)

def trading_day(day: str):
	return datetime.strptime(day, '%Y%m%d').timestamp()

def on_login(trader: QPTrader):
	logging.info('futures-trader ONLINE')

	position = ApiStructure.QryInvestorPositionField(
		BrokerID = env.broker,
		InvestorID = env.investor,
	)
	logging.info('querying position')
	ret = trader.ReqQryInvestorPosition(position, trader.req_id())
	logging.error(f'position ret: {ret}')

_.main(QPTrader, on_login, True)
