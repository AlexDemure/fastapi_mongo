from backend.src.db.settings import MongoDBSettings
from backend.src.apps.statistics.settings import StatisticSettings

# INCLUDE SETTINGS
configs = [MongoDBSettings, StatisticSettings]


class Settings(*configs):
    API_URL: str = "/api/v1"


settings = Settings()

