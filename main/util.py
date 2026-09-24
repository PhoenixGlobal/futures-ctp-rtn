from typing import Any
from fommon.api.qry_position import QryPositionItem

def cook_raw_position(raw: dict[str, Any]):
	return QryPositionItem(
		InstrumentID=raw['InstrumentID'],
		posi_direction=cook_raw_posi_direction(raw['PosiDirection']),
		position_date=cook_raw_position_date(raw['PositionDate']),
		YdPosition=raw['YdPosition'],
		Position=raw['Position'],
		OpenVolume=raw['OpenVolume'],
		CloseVolume=raw['CloseVolume'],
		OpenAmount=raw['OpenAmount'],
		CloseAmount=raw['CloseAmount'],
	)

def cook_raw_posi_direction(raw: str):
	match raw:
		case '1':
			return 'net'
		case '2':
			return 'long'
		case '3':
			return 'short'
		case n:
			return n

def cook_raw_position_date(raw: str):
	match raw:
		case '1':
			return 'today'
		case '2':
			return 'yesterday'
		case n:
			return n
