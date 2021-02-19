import uvicorn
from fastapi import FastAPI

from db.database import dashboards_db
from fixtures import upload_test_data_to_mongodb
from logic import collect_total_data
from schemas import BaseParams, TotalData

app = FastAPI()

dashboards_db.init_connection()


@app.on_event("startup")
async def init_fixtures():
    await upload_test_data_to_mongodb()


@app.post("/statictics/total/", response_model=TotalData)
async def get_total_data(params: BaseParams):
    return await collect_total_data(params)


if __name__ == '__main__':
    uvicorn.run("main:app", host="127.0.0.1", port=7040, log_level="debug")
