from typing import Literal, TypedDict, Callable
from fommon import log

InstrumentStatusReasonKey = Literal['自动切换', '人工切换', '熔断']
class InstrumentStatus(TypedDict):
	trading: bool
	reason: InstrumentStatusReasonKey
	instrument: str

# 订阅者 list[tuple[订阅者名称, 订阅者回调函数]]
__subscriber_list = set[tuple[str, Callable[[InstrumentStatus], None]]]()

# instrument id -> instrument status
__instrument_status_map: dict[str, InstrumentStatus] = {}

# 订阅，返回“取消订阅”
def subscribe(subscriber_name: str, callback: Callable[[InstrumentStatus], None]):
	# TODO: 可以在订阅开始时，推送全量数据
	sub = (subscriber_name, callback)
	__subscriber_list.add(sub)
	return lambda: __subscriber_list.remove(sub)

def update_instrument_status(instrument: str, status_key: str, reason: str):
	__instrument_status_map[instrument] = { # type: ignore
		'trading': status_key == '2',
		'reason': reason,
		'instrument': instrument,
	}
	for subscriber in __subscriber_list:
		try:
			subscriber[1](__instrument_status_map[instrument])
		except Exception as err:
			log.err(f'推送到合约状态订阅者({subscriber[0]})失败')
			log.err2(err)
