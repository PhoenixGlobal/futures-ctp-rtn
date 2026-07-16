from pymongo import MongoClient
import env
from lib.fommon.one import One

def _init_client():
	username, password, host, port = env.mongo
	client = MongoClient(f'mongodb://{username}:{password}@{host}:{port}')
	return client

mongo_client_one = One(
	'mongodb 未初始化',
	_init_client,
	lambda c: c.close(),
)

def db():
	global mongo_client_one
	return mongo_client_one.get()[env.db_name]
