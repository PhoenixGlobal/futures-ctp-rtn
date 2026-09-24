from typing import Any
from fommon.api.qry_position import QryPositionItem

def cook_raw_position(raw: dict[str, Any]):
	data: dict[str, Any] = raw['data']
	return QryPositionItem(
		InstrumentID=data['InstrumentID'],
		posi_direction=cook_raw_posi_direction(data['PosiDirection']),
		position_date=cook_raw_position_date(data['PositionDate']),
		YdPosition=data['YdPosition'],
		Position=data['Position'],
		OpenVolume=data['OpenVolume'],
		CloseVolume=data['CloseVolume'],
		OpenAmount=data['OpenAmount'],
		CloseAmount=data['CloseAmount'],
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
