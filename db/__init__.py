from pymongo import AsyncMongoClient
import env

def _get_db():
	username, password, host, port = env.mongo
	client = AsyncMongoClient(f'mongodb://{username}:{password}@{host}:{port}')
	return client[env.db_name]

db = _get_db()
