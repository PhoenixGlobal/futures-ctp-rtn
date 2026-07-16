from lib.fommon.util import sh_now

# TODO unique request id
# 起始 request_id: 时-分-00001
def req_id_start():
	return int(sh_now().strftime('%H%M') + str(1).zfill(5))
