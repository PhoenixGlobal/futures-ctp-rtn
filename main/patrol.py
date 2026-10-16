# patrol: /pəˈtroʊl/ 巡逻

from asyncio import sleep
from datetime import datetime
from fommon import log
from .ctp.lifecycle import ctp_trader

async def patrol():
	while True:
		now = datetime.now()

		# [JOB] 08:50, 12:50, 20:50 检查 ctp 是否 Ready
		if (now.hour in [8, 12, 20] and now.minute == 50):
			ready_to_trade = ctp_trader.patrol_check()
			if not ready_to_trade:
				log.inf('patrol check: ctp 未 Ready, 已发起 init')
			else:
				log.inf('patrol check: ctp ready to trade')

		await sleep(60)
