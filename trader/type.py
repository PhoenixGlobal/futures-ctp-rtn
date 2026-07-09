from enum import IntEnum
from pydantic import BaseModel

class Direction(IntEnum):
	BUY = 0
	SELL = 1

class Offset(IntEnum):
	OPEN = 0
	CLOSE = 1
	# 由主应用控制平仓时机，这里不区分
	# CLOSE_TODAY = 3
	# CLOSE_YESTERDAY = 4

class PlaceOrder(BaseModel):
	order_id: str
	exchange: str
	instrument: str
	direction: Direction
	offset: Offset
	volume: int
	price_limit: float
