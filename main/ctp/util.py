from ctpwrapper import ApiStructure
from typing import Protocol, Optional
import httpx
from fastapi import HTTPException

from lib.fommon import sh_now
from lib.fommon.api import Direction, PlaceOrder
from lib.fommon.app_config.read import app_config
from ..db import db
from .. import misc

LIMIT_URL = f'http://127.0.0.1:{app_config['orderbook']['port']}/limit/'

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
	misc.log.info(f'{coll_name} (req_id: {req_id}; is_last: {is_last})')
	if (rsp_info is not None) and (rsp_info.ErrorID != 0):
		misc.log.error(rsp_info)

def fetch_price_limit(instrument: str, direction: Direction) -> float:
	url = LIMIT_URL + instrument.lower()
	try:
		r = httpx.get(url, timeout=3.0)
		r.raise_for_status()
		body = r.json()
	except Exception as e:
		raise HTTPException(status_code=502, detail=f'获取涨跌停失败: {e}') from e
	if not body.get('ok') or not isinstance(body.get('data'), dict):
		raise HTTPException(status_code=502, detail=f'获取涨跌停失败: {body}')
	data = body['data']
	key = 'upper' if direction == Direction.BUY else 'lower'
	price = data.get(key)
	if price is None:
		raise HTTPException(status_code=502, detail=f'涨跌停缺少 {key}: {body}')
	misc.log.info(f'涨跌停 {instrument}: upper={data.get("upper")} lower={data.get("lower")} → LimitPrice={price}')
	return float(price)

def new_order(req_id: int, order: PlaceOrder) -> ApiStructure.InputOrderField:
	return ApiStructure.InputOrderField(
		OrderRef = order.order_ref,
		ExchangeID = order.exchange,
		InstrumentID = order.instrument.lower(),
		Direction = str(order.direction.value), # 0: 买; 1: 卖
		CombOffsetFlag = str(order.offset.value), # 0: 开仓; 1: 平仓; 3: 平今; 4: 平昨
		VolumeTotalOriginal = order.volume, # 下单多少手
		LimitPrice = fetch_price_limit(order.instrument, order.direction), # 国君期货：市价单使用限价价格字段作为保护价

		RequestID = req_id,
		BrokerID = app_config['ctp']['broker'],
		InvestorID = app_config['ctp']['investor'],
		UserID = app_config['ctp']['investor'],

		OrderPriceType = '1', # 1: 市价; 2: 限价
		CombHedgeFlag = '1', # 1: 投机;
		TimeCondition = '1', # 1: 立即成交，否则撤单; 3: 当日有效
		VolumeCondition = '1', # 1: 任何数量; 2: 最小数量; 3: 最大数量;
		# MinVolume = 2, # 最小成交量 (在 VolumeCondition 为 “最小数量” 时有效)
		ContingentCondition = '1', # 在什么条件下触发. 1: 立即触发; 2: 止损; 3: 止赢;
		ForceCloseReason = '0', # 0: 非强平
	)