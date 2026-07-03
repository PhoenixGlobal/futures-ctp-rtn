from fastapi import FastAPI
from . import ctp
from .type import PlaceOrder

app = FastAPI()

@app.post('/order')
async def place_order(order: PlaceOrder):
	return _response(
		ctp.place_order(order)
	)

def _response(ok: bool):
	return { 'ok': ok }
