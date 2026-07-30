import inspect
from ctpwrapper import ApiStructure
import env
from lib.fommon.api import PlaceOrder
from lib.fommon import log
from .. import misc
from .util import new_order
from .lifecycle import Lifecycle

def ctp_ret(ret: int):
	fn_name = inspect.currentframe().f_back.f_code.co_name # type: ignore

	ok = ret == 0
	if not ok:
		misc.log.error(f'[{fn_name}] failed, ret: {ret}')
	else:
		misc.log.info(f'[{fn_name}] succeeded, ret: 0')
	return ok

class CTP:
	def __init__(self):
		self.lifecycle = Lifecycle()
	def t(self):
		return self.lifecycle.get()

	def place_order(self, order: PlaceOrder):
		misc.log.info(f'placing order: {order.order_ref}')
		req_id = self.t().req_id()
		input_order = new_order(req_id, order)

		ret = self.t().ReqOrderInsert(input_order, req_id)
		return ctp_ret(ret)

	def settlement(self):
		settlement = ApiStructure.SettlementInfoConfirmField(
			BrokerID = env.broker,
			InvestorID = env.investor,
		)
		log.inf('confirming settlement')
		ret = self.t().ReqSettlementInfoConfirm(settlement, self.t().req_id())
		return ctp_ret(ret)

	def query_account(self):
		input = ApiStructure.QryTradingAccountField(
			BrokerID = env.broker,
			InvestorID = env.investor,
			BizType = '1',
		)
		ret = self.t().ReqQryTradingAccount(input, self.t().req_id())
		return ctp_ret(ret)

	def query_position(self):
		position = ApiStructure.QryInvestorPositionField(
			BrokerID = env.broker,
			InvestorID = env.investor,
		)
		ret = self.t().ReqQryInvestorPosition(position, self.t().req_id())
		return ctp_ret(ret)

ctp = CTP()
