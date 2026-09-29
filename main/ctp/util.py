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
	upper_limit: float  # 涨停板价格
	lower_limit: float  # 跌停板价格
	banding_upper: float  # 动态价格波动上限
	banding_lower: float  # 动态价格波动下限
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

	price, source = __protect_price(instrument, data, direction)
	log.inf(f'保护价({instrument}: {source}) → LimitPrice={price:.2f}')
	__print_orderbook(data)
	return price

def __product(instrument: str) -> str:
	i = 0
	while i < len(instrument) and instrument[i].isalpha():
		i += 1
	return instrument[:i]

def __clamp_protect(price: float, data: PriceLimitData, is_buy: bool) -> float:
	"""报单价必须同时落在涨跌停与动态波动限制（有值时）内。"""
	if is_buy:
		price = min(price, data.upper_limit)
		if data.banding_upper != 0:
			price = min(price, data.banding_upper)
	else:
		price = max(price, data.lower_limit)
		if data.banding_lower != 0:
			price = max(price, data.banding_lower)
	return price

def __protect_price(instrument: str, data: PriceLimitData, direction: Direction) -> tuple[float, str]:
	"""
	保护价：先按盘口算激进候选价，最后统一夹紧。
	涨跌停单独当保护价易撞动态波动限制；banding 行情里常为 0，不能依赖。
	"""
	is_buy = direction == Direction.BUY
	book = data.ask if is_buy else data.bid
	product = __product(instrument)

	banding = data.banding_upper if is_buy else data.banding_lower
	if banding != 0:
		# 有有效 banding 时，取允许范围内最激进价（务必成交）
		candidate, source = banding, '动态波动限制'
	elif product in {'IC', 'IM'} and len(book) >= 1:
		# 中金所股指盘口常只有 1 档：对手价 ±10 tick
		offset = 10 * 0.2
		candidate = book[0][0] + (offset if is_buy else -offset)
		source = f'{product} 第1档±10tick'
	elif len(book) >= 5:
		candidate, source = book[4][0], '第5档行情'
	elif len(book) >= 1:
		candidate, source = book[-1][0], f'第{len(book)}档行情'
	else:
		# 无盘口才退回涨跌停（仍可能被动态限制拒单）
		candidate = data.upper_limit if is_buy else data.lower_limit
		source = '涨跌停(无盘口)'

	return __clamp_protect(candidate, data, is_buy), source

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