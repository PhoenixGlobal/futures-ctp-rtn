from pymongo import MongoClient
from pymongo.database import Database
from lib.fommon.singleton import Singleton
from lib.fommon import log
from lib.fommon.app_config.const import conn_str, db_name__ctp

class Lifecycle(Singleton[MongoClient]):
	def _create(self):
		log.inf(f'connecting to {conn_str}')
		client = MongoClient(conn_str)
		return client
	def _destroy(self, instance: MongoClient):
		instance.close()

class DB:
	def __init__(self):
		self.lifecycle = Lifecycle()
	def _(self) -> Database:
		return self.lifecycle.get()[db_name__ctp]

	def insert_one(self, coll: str, data: dict):
		self._()[coll].insert_one(data)

db = DB()
