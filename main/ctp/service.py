from fommon.api import PlaceOrder
from fommon import log

from ._util import new_order
from .lifecycle import ctp_trader

def place_order(order: PlaceOrder):
	log.inf(f'正在下单: {order.order_ref}')
	input_order = new_order(ctp_trader.req_id(), order)
	log.inf(input_order)
	ctp_trader.place_order(input_order)
