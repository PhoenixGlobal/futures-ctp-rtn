from ctpwrapper import ApiStructure
from typing import Protocol, Optional

from fommon import sh_now, log
from fommon.api import PlaceOrder
from fommon.app_config.read import app_config
from ..db import db

class DictLike(Protocol):
	def to_dict(self) -> dict:
		return {}

def save(
	coll_name: str,
	data: DictLike,
	rsp_info: Optional[ApiStructure.RspInfoField] = None,
	req_id: int = 0,
	is_last: Optional[bool] = None,
):
	db.insert_one(coll_name, {
		'data': data.to_dict(),
		'rsp_info': rsp_info and rsp_info.to_dict(),
		'req_id': req_id,
		'is_last': is_last,
		'timestamp': sh_now(),
	})
	log.inf(f'{coll_name} (req_id: {req_id}; is_last: {is_last})')
	if (rsp_info is not None) and (rsp_info.ErrorID != 0):
		log.err(rsp_info)


def new_order(req_id: int, order: PlaceOrder) -> ApiStructure.InputOrderField:
	return ApiStructure.InputOrderField(
		OrderRef = str(order.order_ref),
		ExchangeID = order.exchange,
		InstrumentID = order.instrument,
		Direction = str(order.direction.value), # 0: 买; 1: 卖
		CombOffsetFlag = str(order.offset.value), # 0: 开仓; 1: 平仓; 3: 平今; 4: 平昨
		VolumeTotalOriginal = order.volume, # 下单多少手
		LimitPrice = order.price_limit,

		RequestID = req_id,
		BrokerID = app_config['ctp']['broker'],
		InvestorID = app_config['ctp']['investor'],
		UserID = app_config['ctp']['investor'],

		OrderPriceType = '2', # 1: 市价; 2: 限价
		CombHedgeFlag = '1', # 1: 投机;
		TimeCondition = '1', # 1: 立即成交，否则撤单; 3: 当日有效
		VolumeCondition = '1', # 1: 任何数量; 2: 最小数量; 3: 最大数量;
		# MinVolume = 2, # 最小成交量 (在 VolumeCondition 为 “最小数量” 时有效)
		ContingentCondition = '1', # 在什么条件下触发. 1: 立即触发; 2: 止损; 3: 止赢;
		ForceCloseReason = '0', # 0: 非强平
	)
