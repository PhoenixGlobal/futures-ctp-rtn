import logging
from datetime import datetime
from ctp.trader import BaseTrader
from ctpwrapper import ApiStructure
import env
from . import _

class QATrader(BaseTrader):
	def OnRspQryTradingAccount(self, account: ApiStructure.TradingAccount, pRspInfo, nRequestID, bIsLast):
		logging.info('\n\n当前账户')
		# logging.info(account)
		logging.info(f'balance: {account.Balance:.2f}')
		logging.info(f'available: {account.Available:.2f}')
		logging.info(f'frozen margin: {account.FrozenMargin:.2f}')
		logging.info(f'current margin: {account.CurrMargin:.2f}')

def on_login(trader: QATrader):
	logging.info('futures-trader ONLINE')
	logging.info('querying account')

	input = ApiStructure.QryTradingAccountField(
		BrokerID = env.broker,
		InvestorID = env.investor,
		BizType = 1,
	)
	ret = trader.ReqQryTradingAccount(input, trader.req_id())
	logging.error(f'query account ret: {ret}')

_.main(QATrader, on_login, True)
