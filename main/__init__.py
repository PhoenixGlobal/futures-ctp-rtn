from time import sleep
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fommon.api import PlaceOrder
from fommon import log, http
from .db import db
from .ctp import lifecycle as ctp_lc, util as ctp_util
from . import util

@asynccontextmanager
async def lifespan(_: FastAPI):
	db.lifecycle.init()
	ctp_lc.init()
	yield
	db.lifecycle.clear()
	ctp_lc.clear()

app = FastAPI(lifespan = lifespan)
trader = ctp_lc.ctp_trader

@app.post('/order')
async def place_order(order: PlaceOrder):
	log.inf(f'收到下单命令: {order}')
	input_order = ctp_util.new_order(trader.req_id(), order)
	log.inf(input_order)
	trader.place_order(input_order)
	log.inf(f'订单已发送到 CTP({order.order_ref})')
	return http.respond_success()

@app.get('/trading-day')
def get_trading_day():
	return http.respond_success(
		trader.GetTradingDay()
	)

@app.get('/position')
def get_position():
	rid = trader.query_position()
	retry = 0
	while True:
		if retry > 10:
			return http.respond_error(f'查询仓位失败, retry_count: {retry}')
		retry += 1

		log.inf(f'查询仓位(request id: {rid})...')
		sleep(.2)
		p_list = db.get_qry_position(rid)
		if len(p_list) == 0:
			continue
		if p_list[-1]['is_last'] == False:
			continue
		data = [util.cook_raw_position(p) for p in p_list]
		log.inf('\n'.join(str(p) for p in data if p.position_date == 'today'))
		return http.respond_success(data)
