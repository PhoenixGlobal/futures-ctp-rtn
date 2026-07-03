from pymongo import MongoClient
import env

def _get_db():
	username, password, host, port = env.mongo
	client = MongoClient(f'mongodb://{username}:{password}@{host}:{port}')
	return client[env.db_name]

db = _get_db()
