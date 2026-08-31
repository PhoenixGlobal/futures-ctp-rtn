import uvicorn
from lib.fommon.app_config.read import app_config

if __name__ == '__main__':
	config = app_config['trade']
	print(f'期货(trade) 启动 {config}')

	uvicorn.run(
		'main:app',
		host='0.0.0.0' if config['dev'] else '127.0.0.1',
		port=config['port'],
		reload=config['dev'],
	)
