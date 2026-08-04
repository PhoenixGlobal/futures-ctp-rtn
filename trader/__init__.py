from contextlib import asynccontextmanager
from fastapi import FastAPI
from lib.fommon.api import PlaceOrder
from lib.fommon import log
from .db import db
from .ctp import ctp

@asynccontextmanager
async def lifespan(_: FastAPI):
	db.lifecycle.init()
	ctp.lifecycle.init()
	yield
	db.lifecycle.clear()
	ctp.lifecycle.clear()

app = FastAPI(lifespan = lifespan)

@app.post('/order')
async def place_order(order: PlaceOrder):
	log.inf(f'收到下单命令     {order}')
	return _response(
		ctp.place_order(order)
	)

# @app.post('/settlement')
# async def settlement():
# 	return _response(
# 		ctp.settlement()
# 	)

@app.post('/query_account')
async def query_account():
	return _response(
		ctp.query_account()
	)

@app.post('/query_position')
async def query_position():
	return _response(
		ctp.query_position()
	)

def _response(ok: bool):
	return { 'ok': ok }
