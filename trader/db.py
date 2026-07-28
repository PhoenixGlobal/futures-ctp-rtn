from pymongo import MongoClient
from pymongo.database import Database
import env
from lib.fommon.singleton import Singleton
from lib.fommon import log

class Lifecycle(Singleton[MongoClient]):
	def _create(self):
		conn = f'mongodb://127.0.0.1:{env.mongo['port']}'
		log.inf(f'connecting to {conn}')
		client = MongoClient(conn)
		return client
	def _destroy(self, instance: MongoClient):
		return instance.close()

class DB:
	def __init__(self):
		self.lifecycle = Lifecycle()
	def _(self) -> Database:
		return self.lifecycle.get()[env.mongo['db_name']]

	def insert_one(self, coll: str, data: dict):
		self._()[coll].insert_one(data)

db = DB()
