from ctpwrapper import ApiStructure
from trader.ctp import Trader
import env
from . import _

def place_order(trader: Trader):
	req_id = trader.req_id()
	order = ApiStructure.InputOrderField(
		OrderRef = 'tensor-test',
		RequestID = req_id,

		BrokerID = env.broker,
		InvestorID = env.investor,
		UserID = env.investor,

		OrderPriceType = 1, # 1: 市价; 2: 限价
		# LimitPrice = 891,
		Direction = 1, # 0: 卖; 1: 买
		CombOffsetFlag = 0, # 0: 开仓; 1: 平仓; 3: 平今; 4: 平昨
		CombHedgeFlag = 1, # 1: 投机;
		VolumeTotalOriginal = 1, # 下单多少手
		TimeCondition = 1, # 1: 立即成交，否则撤单; 3: 当日有效
		VolumeCondition = 1, # 1: 任何数量; 2: 最小数量; 3: 最大数量;
		# MinVolume = 2, # 最小成交量 (在 VolumeCondition 为 “最小数量” 时有效)
		ContingentCondition = 1, # 在什么条件下触发. 1: 立即触发; 2: 止损; 3: 止赢;
		ForceCloseReason = 0, # 0: 非强平
		ExchangeID = 'SHFE',
		InstrumentID = 'au2608',
	)
	ret = trader.ReqOrderInsert(order, req_id)
	trader.log.info(f'下单: {ret}')

_.main(Trader, place_order, True)
