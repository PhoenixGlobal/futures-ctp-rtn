from datetime import datetime
from zoneinfo import ZoneInfo

def sh_now():
	return datetime.now(ZoneInfo('Asia/Shanghai'))
