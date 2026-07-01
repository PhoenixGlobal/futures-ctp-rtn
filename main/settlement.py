import logging
from ctp.trader import Trader
from ctpwrapper import ApiStructure
import env

def main():
	logging.basicConfig(level=logging.INFO)
	trader = Trader()
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

	if trader.login == False:
		logging.error('trader login failed')
		return

	logging.info('futures-trader ONLINE')

	settlement = ApiStructure.SettlementInfoConfirmField(
		BrokerID = env.broker,
		InvestorID = env.investor,
	)
	logging.info('confirming settlement')
	ret = trader.ReqSettlementInfoConfirm(settlement, trader.req_id())
	if ret != 1:
		logging.error(f'settlement failed: {ret}')

main()
