import asyncio
from time import sleep
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fommon.api import PlaceOrder
from fommon import log, http, sh_now
from .db import db
from .ctp import lifecycle as ctp_lc, util as ctp_util
from . import util
from . import instrument_status

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
	time_limit = sh_now()
	rid = trader.query_position()
	retry = 0
	while True:
		if retry > 10:
			return http.respond_error(f'查询仓位失败, retry_count: {retry}')
		retry += 1

		sleep(.2)
		p_list = db.get_qry_position(rid, time_limit)
		if len(p_list) == 0:
			continue
		if p_list[-1]['is_last'] == False:
			continue
		data = [util.cook_raw_position(p) for p in p_list]
		return http.respond_success(data)

@app.websocket('/subscribe_instrument_status/{subscriber_name}')
async def subscribe_instrument_status(websocket: WebSocket, subscriber_name: str):
	await websocket.accept()

	loop = asyncio.get_running_loop()
	def push(status: instrument_status.InstrumentStatus):
		asyncio.run_coroutine_threadsafe(
			websocket.send_json(status),
			loop,
		)
	log.inf(f'合约交易状态订阅者({subscriber_name})已连接')
	unsubscribe = instrument_status.subscribe(subscriber_name, push)

	try:
		while True:
			await websocket.receive_text()
	except WebSocketDisconnect:
		log.inf(f'合约交易状态订阅者({subscriber_name})断开连接')
		unsubscribe()
