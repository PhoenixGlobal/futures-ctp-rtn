from ..type import PlaceOrder
from .. import misc
from .trader import init_trader
from .util import new_order

_trader = init_trader()

def place_order(order: PlaceOrder):
	misc.log.info(f'placing order: {order.order_id}')
	req_id = _trader.req_id()
	input_order = new_order(req_id, order)

	ret = _trader.ReqOrderInsert(input_order, req_id)
	ok = ret == 0
	if not ok:
		misc.log.error(f'place order failed, ret: {ret}')
	misc.log.info('place order ret: 0')
	return ok
