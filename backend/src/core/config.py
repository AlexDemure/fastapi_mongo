from backend.src.db.settings import MongoDBSettings

# INCLUDE SETTINGS
configs = [MongoDBSettings]


class Settings(*configs):
    API_URL: str = "/api/v1"


settings = Settings()

