import os
import motor.motor_asyncio
from pymongo import MongoClient

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")

class AsyncDB:
    def __init__(self):
        self._client = None
        self._db = None
        
    @property
    def client(self):
        if self._client is None:
            self._client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
        return self._client
        
    @property
    def db(self):
        if self._db is None:
            self._db = self.client.darkintelliweb
        return self._db
        
    def reset(self):
        self._client = None
        self._db = None
        
    def __getattr__(self, name):
        return getattr(self.db, name)

db = AsyncDB()

sync_client = MongoClient(MONGO_URI)
sync_db = sync_client.darkintelliweb
