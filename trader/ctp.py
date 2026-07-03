from ctpwrapper import ApiStructure
from ctp.trader import BaseTrader
import util
import env
from .type import PlaceOrder, Direction, Offset
from .db import db
from . import misc

class Trader(BaseTrader):
	def __init__(self):
		def after_login(_):
			misc.log.info('ctp trader logged in')
		super().__init__(after_login, misc.log_name)
	
	# 期货公司响应
	def OnRspOrderInsert(self, pInputOrder, pRspInfo, nRequestID, bIsLast):
		self.log.info('OnRspOrderInsert')
		self.log.info(nRequestID)

	# 订单实时状态推送
	def OnRtnOrder(self, pOrder: ApiStructure.OrderField):
		self.log.info(f'OnRtnOrder (req_id: {pOrder.RequestID})')
		db['RtnOrder'].insert_one({
			'data': pOrder.to_dict(),
			'timestamp': util.now(),
		})
		self.log.info(f'RtnOrder (req_id: {pOrder.RequestID}) saved')

	# 报单插入错误（交易所）
	def OnErrRtnOrderInsert(self, pInputOrder, pRspInfo):
		self.log.error('order insert failed')
		self.log.error(pInputOrder)
		self.log.error(pRspInfo)

	# 成交
	def OnRtnTrade(self, pTrade) -> None:
		self.log.info('OnRtnTrade')
		self.log.info(pTrade)

def _init_trader():
	misc.log.info('initing ctp trader')
	trader = Trader()
	trader.Create()
	ip, port = env.trader_server
	trader.RegisterFront(f'tcp://{ip}:{port}')
	trader.SubscribePrivateTopic(
		1, # 从上次断开后发
		8888, # SubscribePrivateTopic 未用到这个参数，我瞎写的
	)
	trader.Init()

	misc.log.info(f'ctp trader initialized, trading day: {trader.GetTradingDay()}')
	return trader

_trader = _init_trader()

def _new_order(req_id: int, order: PlaceOrder) -> ApiStructure.InputOrderField:
	return ApiStructure.InputOrderField(
		OrderRef = order.order_id,
		ExchangeID = order.exchange,
		InstrumentID = order.instrument,
		Direction = order.direction.value, # 0: 卖; 1: 买
		CombOffsetFlag = order.offset.value, # 0: 开仓; 1: 平仓; 3: 平今; 4: 平昨
		VolumeTotalOriginal = order.volume, # 下单多少手

		RequestID = req_id,
		BrokerID = env.broker,
		InvestorID = env.investor,
		UserID = env.investor,

		OrderPriceType = 1, # 1: 市价; 2: 限价
		# LimitPrice = 891,
		CombHedgeFlag = 1, # 1: 投机;
		TimeCondition = 1, # 1: 立即成交，否则撤单; 3: 当日有效
		VolumeCondition = 1, # 1: 任何数量; 2: 最小数量; 3: 最大数量;
		# MinVolume = 2, # 最小成交量 (在 VolumeCondition 为 “最小数量” 时有效)
		ContingentCondition = 1, # 在什么条件下触发. 1: 立即触发; 2: 止损; 3: 止赢;
		ForceCloseReason = 0, # 0: 非强平
	)

def place_order(order: PlaceOrder):
	misc.log.info(f'placing order: {order.order_id}')
	req_id = _trader.req_id()
	new_order = _new_order(req_id, order)

	ret = _trader.ReqOrderInsert(new_order, req_id)
	ok = ret == 0
	if not ok:
		misc.log.error(f'place order failed, ret: {ret}')
	return ok
