from ctpwrapper import ApiStructure
import env
from util import One
from ..type import PlaceOrder
from .. import misc
from .trader import init_trader
from .util import new_order

one = One(
	'trader 未初始化',
	init_trader,
	lambda t: t.Release(),
)

def _ctp_ret(ret: int, name: str):
	ok = ret == 0
	if not ok:
		misc.log.error(f'[{name}] failed, ret: {ret}')
	else:
		misc.log.info(f'[{name}] succeeded, ret: 0')
	return ok

def place_order(order: PlaceOrder):
	global one
	trader = one.get()
	misc.log.info(f'placing order: {order.order_id}')
	req_id = trader.req_id()
	input_order = new_order(req_id, order)

	ret = trader.ReqOrderInsert(input_order, req_id)
	return _ctp_ret(ret, 'placing order')

def settlement():
	global one
	trader = one.get()
	settlement = ApiStructure.SettlementInfoConfirmField(
		BrokerID = env.broker,
		InvestorID = env.investor,
	)
	trader.log.info('confirming settlement')
	ret = trader.ReqSettlementInfoConfirm(settlement, trader.req_id())
	return _ctp_ret(ret, 'settlement')
