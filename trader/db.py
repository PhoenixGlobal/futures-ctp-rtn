from pymongo import MongoClient
from pymongo.database import Database
import env
from lib.fommon.singleton import Singleton

class Lifecycle(Singleton[MongoClient]):
	def _create(self):
		username, password, host, port = env.mongo
		client = MongoClient(f'mongodb://{username}:{password}@{host}:{port}')
		return client
	def _destroy(self, instance: MongoClient):
		return instance.close()

class DB:
	def __init__(self):
		self.lifecycle = Lifecycle()
	def _(self) -> Database:
		return self.lifecycle.get()['futures-ctp']

	def insert_one(self, coll: str, data: dict):
		self._()[coll].insert_one(data)

db = DB()
