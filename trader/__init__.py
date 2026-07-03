from fastapi import FastAPI
from fastapi.requests import Request
from .misc import log

app = FastAPI()

@app.get('/order')
async def place_order(req: Request):
	print(req.query_params)
	log.info('test')
	log.error('errro')
	return { "message": "hello" }
