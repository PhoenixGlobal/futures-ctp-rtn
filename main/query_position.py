import logging
from datetime import datetime
from ctp.trader import BaseTrader
from ctpwrapper import ApiStructure
import env
from . import _

class QPTrader(BaseTrader):
	def OnRspQryInvestorPosition(self, pos: ApiStructure.InvestorPositionField, pRspInfo, nRequestID, bIsLast):
		logging.info(f'当前仓位, bIsLast: {bIsLast}')
		# logging.info(pos)
		# logging.info(pRspInfo)
		logging.info(
			f'instrument: {pos.InstrumentID}; '
			f'direction: {pos.PosiDirection}; '
			f'昨仓: {pos.YdPosition}; '
			f'今仓: {pos.Position}.'
		)

def trading_day(day: str):
	return datetime.strptime(day, '%Y%m%d').timestamp()

def on_login(trader: QPTrader):
	logging.info('futures-trader ONLINE')

	position = ApiStructure.QryInvestorPositionField(
		BrokerID = env.broker,
		InvestorID = env.investor,
	)
	logging.info('querying position')
	logging.info('!! pos direction: 1 净, 2 多, 3 空')
	ret = trader.ReqQryInvestorPosition(position, trader.req_id())
	logging.error(f'position ret: {ret}')

_.main(QPTrader, on_login, True)
