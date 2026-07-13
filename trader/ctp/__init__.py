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

def place_order(order: PlaceOrder):
	global one
	trader = one.get()
	misc.log.info(f'placing order: {order.order_id}')
	req_id = trader.req_id()
	input_order = new_order(req_id, order)

	ret = trader.ReqOrderInsert(input_order, req_id)
	ok = ret == 0
	if not ok:
		misc.log.error(f'place order failed, ret: {ret}')
	misc.log.info('place order ret: 0')
	return ok
