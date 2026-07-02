import logging
from ctp.trader import BaseTrader
from ctpwrapper import ApiStructure
import env
from . import _

class SettlementTrader(BaseTrader):
	def OnRspSettlementInfoConfirm(self, pSettlementInfoConfirm, pRspInfo, nRequestID, bIsLast):
		logging.info(f'settlement info confirmed:')
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

def main():
	logging.basicConfig(level=logging.INFO)
	trader = SettlementTrader(on_login)
	trader.Create()
	ip, port = env.trader_server
	logging.info(f'registering front: {ip}:{port}')
	trader.RegisterFront(f'tcp://{ip}:{port}')
	trader.SubscribePrivateTopic(
		1, # 从上次断开后发
		8888, # SubscribePrivateTopic 未用到这个参数，我瞎写的
	)
	trader.Init()
	logging.info(f'trading day: {trader.GetTradingDay()}')
	_.hold()

def on_login(trader: SettlementTrader):
	logging.info('futures-trader ONLINE')

	settlement = ApiStructure.SettlementInfoConfirmField(
		BrokerID = env.broker,
		InvestorID = env.investor,
	)
	logging.info('confirming settlement')
	ret = trader.ReqSettlementInfoConfirm(settlement, trader.req_id())
	logging.error(f'settlement ret: {ret}')

main()
