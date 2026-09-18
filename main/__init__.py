from contextlib import asynccontextmanager
from fastapi import FastAPI
from fommon.api import PlaceOrder
from fommon import log
from .db import db
from .ctp import lifecycle as ctp_lc, service as ctp_svc

@asynccontextmanager
async def lifespan(_: FastAPI):
	db.lifecycle.init()
	ctp_lc.init()
	yield
	db.lifecycle.clear()
	ctp_lc.clear()

app = FastAPI(lifespan = lifespan)

@app.post('/order')
async def place_order(order: PlaceOrder):
	log.inf(f'收到下单命令     {order}')
	ctp_svc.place_order(order)
	return _response(True)

def _response(ok: bool):
	return { 'ok': ok }
