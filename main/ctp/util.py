from ctpwrapper import ApiStructure
from typing import Protocol, Optional
import httpx
from fastapi import HTTPException
from pydantic import BaseModel

from fommon import sh_now, log
from fommon.api import Direction, PlaceOrder
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

class PriceLimitData(BaseModel):
	top: float
	bottom: float
	bid: list[tuple[float, int]] # tuple[价格, 数量]
	ask: list[tuple[float, int]]
class PriceLimitResponse(BaseModel):
	ok: bool
	data: PriceLimitData

def fetch_price_limit(instrument: str, direction: Direction) -> float:
	url = f'http://127.0.0.1:{app_config['md']['port']}/price-limit?instrument={instrument}'
	try:
		r = httpx.get(url, timeout=3.0)
		r.raise_for_status()
		body = r.json()
		data = PriceLimitResponse.model_validate(body).data
	except Exception as e:
		log.err2(f'获取涨跌停失败: {e}')
		raise HTTPException(status_code=502) from e

	# __print_orderbook(data)
	# log.inf(f'涨跌停({instrument}: {data.bottom:.2f} ~ {data.top:.2f}) → LimitPrice={price:.2f}')
	limit = data.ask if direction == Direction.BUY else data.bid
	assert len(limit) != 0, f'盘口不足({instrument})，无法获取价格保护'
	__print_price_limit(limit)

	result = limit[-1][0]
	if direction == Direction.BUY:
		result += 0.1
	else:
		result -= 0.1
	return result

def __print_price_limit(limit: list[tuple[float, int]]):
	formatted = [f'{p[0]:.2f}x{p[1]}' for p in limit]
	log.inf(f'盘口: {formatted} ==> {formatted[-1]}')

def __print_orderbook(data: PriceLimitData):
	ask = [f'{p[0]:.2f}x{p[1]}' for p in data.ask]
	bid = [f'{p[0]:.2f}x{p[1]}' for p in data.bid]
	log.inf(f'ask: {", ".join(ask)}')
	log.inf(f'bid: {", ".join(bid)}')

def new_order(req_id: int, order: PlaceOrder) -> ApiStructure.InputOrderField:
	return ApiStructure.InputOrderField(
		OrderRef = str(order.order_ref),
		ExchangeID = order.exchange,
		InstrumentID = order.instrument,
		Direction = str(order.direction.value), # 0: 买; 1: 卖
		CombOffsetFlag = str(order.offset.value), # 0: 开仓; 1: 平仓; 3: 平今; 4: 平昨
		VolumeTotalOriginal = order.volume, # 下单多少手
		LimitPrice = fetch_price_limit(order.instrument, order.direction), # 国君期货：市价单使用限价价格字段作为保护价

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