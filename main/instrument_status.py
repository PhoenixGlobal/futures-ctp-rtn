from typing import Literal, TypedDict

InstrumentStatusReasonKey = Literal['自动切换', '人工切换', '熔断']
class InstrumentStatus(TypedDict):
	trading: bool
	reason: InstrumentStatusReasonKey

# instrument id -> instrument status
instrument_status_map: dict[str, InstrumentStatus] = {}
