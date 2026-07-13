from contextlib import asynccontextmanager
from fastapi import FastAPI
from . import ctp, db
from .type import PlaceOrder

@asynccontextmanager
async def lifespan(_: FastAPI):
	db.mongo_client_one.init()
	ctp.one.init()
	yield
	db.mongo_client_one.clear()
	ctp.one.clear()

app = FastAPI(lifespan = lifespan)

@app.post('/order')
async def place_order(order: PlaceOrder):
	return _response(
		ctp.place_order(order)
	)

@app.post('/settlement')
async def settlement():
	return _response()

def _response(ok: bool):
	return { 'ok': ok }
