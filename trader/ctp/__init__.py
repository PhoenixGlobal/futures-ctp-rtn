import inspect
from ctpwrapper import ApiStructure
import env
from lib.fommon.one import One
from lib.fommon.api import PlaceOrder
from .. import misc
from .trader import init_trader
from .util import new_order

one = One(
	'trader 未初始化',
	init_trader,
	lambda t: t.Release(),
)
_t = lambda: one.get()

def _ctp_ret(ret: int):
	fn_name = inspect.currentframe().f_back.f_code.co_name # type: ignore

	ok = ret == 0
	if not ok:
		misc.log.error(f'[{fn_name}] failed, ret: {ret}')
	else:
		misc.log.info(f'[{fn_name}] succeeded, ret: 0')
	return ok

def place_order(order: PlaceOrder):
	misc.log.info(f'placing order: {order.order_id}')
	req_id = _t().req_id()
	input_order = new_order(req_id, order)

	ret = _t().ReqOrderInsert(input_order, req_id)
	return _ctp_ret(ret)

def settlement():
	settlement = ApiStructure.SettlementInfoConfirmField(
		BrokerID = env.broker,
		InvestorID = env.investor,
	)
	_t().log.info('confirming settlement')
	ret = _t().ReqSettlementInfoConfirm(settlement, _t().req_id())
	return _ctp_ret(ret)

def query_account():
	input = ApiStructure.QryTradingAccountField(
		BrokerID = env.broker,
		InvestorID = env.investor,
		BizType = '1',
	)
	ret = _t().ReqQryTradingAccount(input, _t().req_id())
	return _ctp_ret(ret)

def query_position():
	position = ApiStructure.QryInvestorPositionField(
		BrokerID = env.broker,
		InvestorID = env.investor,
	)
	ret = _t().ReqQryInvestorPosition(position, _t().req_id())
	return _ctp_ret(ret)
