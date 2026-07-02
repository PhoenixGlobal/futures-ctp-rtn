from datetime import datetime
from zoneinfo import ZoneInfo

def now():
	return datetime.now(ZoneInfo('Asia/Shanghai'))

# 起始 request_id: 时-分-00001
def req_id_start():
	return int(now().strftime('%H%M') + str(1).zfill(5))
