import logging
from ctp.trader import BaseTrader
from ctpwrapper import ApiStructure
from lib.fommon.app_config.read import app_config
from . import _

class QATrader(BaseTrader):
	def OnRspQryTradingAccount(self, pTradingAccount: ApiStructure.TradingAccountField, pRspInfo, nRequestID, bIsLast):
		logging.info('\n\n当前账户')
		# logging.info(pTradingAccount)
		logging.info(f'balance: {pTradingAccount.Balance:.2f}')
		logging.info(f'available: {pTradingAccount.Available:.2f}')
		logging.info(f'frozen margin: {pTradingAccount.FrozenMargin:.2f}')
		logging.info(f'current margin: {pTradingAccount.CurrMargin:.2f}')

def on_login(trader: QATrader):
	logging.info('futures-trader ONLINE')
	logging.info('querying account')

	input = ApiStructure.QryTradingAccountField(
		BrokerID = app_config['ctp']['broker'],
		InvestorID = app_config['ctp']['investor'],
		BizType = '1',
	)
	ret = trader.ReqQryTradingAccount(input, trader.req_id())
	logging.error(f'query account ret: {ret}')

_.main(QATrader, on_login, True)
