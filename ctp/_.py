import util

# 起始 request_id: 时-分-00001
def req_id_start():
	return int(util.now().strftime('%H%M') + str(1).zfill(5))

if __name__ == '__main__':
	print(req_id_start())
