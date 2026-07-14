import inspect
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Optional, Callable

def sh_now():
	return datetime.now(ZoneInfo('Asia/Shanghai'))

class One[T]:
	_: Optional[T] = None
	_err_msg: str
	_init: Callable[[], T]
	_clear: Callable[[T], None]

	def __init__(
		self,
		err_msg: str,
		init: Callable[[], T],
		clear: Callable[[T], None],
	):
		self._err_msg = err_msg
		self._init = init
		self._clear = clear

	def init(self):
		if self._ is not None:
			raise Exception('重复初始化')
		self._ = self._init()

	def get(self) -> T:
		if self._ is None:
			raise Exception(self._err_msg)
		return self._

	def clear(self):
		self._clear(self.get())
