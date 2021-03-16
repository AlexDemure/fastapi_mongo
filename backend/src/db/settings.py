import os
from typing import Optional
from pydantic import BaseSettings, validator


class MongoDBSettings(BaseSettings):
    mongo_username = os.environ.get('MONGO_INITDB_ROOT_USERNAME', 'root')
    mongo_password = os.environ.get('MONGO_INITDB_ROOT_PASSWORD', 'rootpassword')
    mongo_host = os.environ.get('MONGO_HOST', 'mongodb')
    mongo_port = os.environ.get('MONGO_PORT', '27017')

    mongo_uri: Optional[str] = None

    def get_uri(self):
        return f"mongodb://{self.mongo_username}:{self.mongo_password}@{self.mongo_host}:{self.mongo_port}/"
