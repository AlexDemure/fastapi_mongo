import uvicorn
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.src.apps.xlsx.fixtures import upload_statistic_data_to_mongodb
from backend.src.core.config import settings
from backend.src.core.urls import api_router
from backend.src.db.database import dashboards_db
from backend.src.utils import run_function_in_separate_thread

app = FastAPI()

dashboards_db.init_connection()


def apscheduler():
    scheduler = AsyncIOScheduler(timezone='Europe/Moscow')
    scheduler.add_job(
        func=run_function_in_separate_thread,
        trigger='cron',
        hour=12,
        minute=45,
        args=(upload_statistic_data_to_mongodb,)
    )
    scheduler.start()


apscheduler()


app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


app.include_router(api_router, prefix=settings.API_URL)


if __name__ == '__main__':
    uvicorn.run("application:app", host="0.0.0.0", port=7040, log_level="debug")

