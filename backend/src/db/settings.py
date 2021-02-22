import os
from typing import Optional
from pydantic import BaseSettings, validator


class MongoDBSettings(BaseSettings):
    mongo_username = os.environ['MONGO_INITDB_ROOT_USERNAME']
    mongo_password = os.environ['MONGO_INITDB_ROOT_PASSWORD']
    mongo_host = os.environ['MONGO_HOST']
    mongo_port = os.environ['MONGO_PORT']

    mongo_uri: Optional[str] = None

    def get_uri(self):
        return f"mongodb://{self.mongo_username}:{self.mongo_password}@{self.mongo_host}:{self.mongo_port}/"
