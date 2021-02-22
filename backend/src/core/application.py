import uvicorn
from fastapi import FastAPI

from backend.src.db.database import dashboards_db
from backend.src.fixtures import upload_test_data_to_mongodb
from backend.src.core.config import settings
from backend.src.core.urls import api_router

app = FastAPI()

dashboards_db.init_connection()


@app.on_event("startup")
async def init_fixtures():
    await upload_test_data_to_mongodb()


app.include_router(api_router, prefix=settings.API_URL)


if __name__ == '__main__':
    uvicorn.run("application:app", host="127.0.0.1", port=7040, log_level="debug")

