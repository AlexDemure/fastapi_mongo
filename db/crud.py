from typing import Optional
from datetime import datetime
from db.database import dashboards_db
from overrides import get_datetime_start_day


async def get_count_documents_by_date_today():
    """Поиск загруженных документов за сегодняшний день."""
    return await dashboards_db.collection.count_documents({'uploaded_at': get_datetime_start_day()})


async def add_many_documents(documents: list):
    """Множественная загрузка документов за один заход."""
    await dashboards_db.collection.insert_many(documents)  # Множественная загрузка в БД


async def get_total_data_by_period(books: list, period: datetime = None) -> Optional[dict]:
    """Получение данных за весь период."""

    pipeline = [
        {
            '$match': {
                '$and': [
                    {'isbn': {
                        "$in": books}
                    },
                    {'uploaded_at': {
                        "$lte": period if period is not None else get_datetime_start_day()
                    }}
                ]
            }
        },
        {
            '$group': {
                '_id': None,
                'total_hours': {
                    '$sum': "$hours"
                },
                'total_listeners': {
                    '$sum': "$started"
                },
                'avg_finishing': {
                    '$avg': "$finishing_rate"
                },

            }
        }
    ]
    async for document in dashboards_db.collection.aggregate(pipeline):
        return document

# pipeline = [
#         {
#             '$match': {
#                 '$and': [
#                     {'isbn': {
#                         "$in": books}
#                     },
#                     {'uploaded_at': {
#                         "$gt": get_datetime_start_day()
#                     }}
#                 ]
#             }
#         },
#         {
#             '$group': {
#                 '_id': {'isbn': "$isbn", 'uploaded_at': "$uploaded_at"},
#                 'totalHours': {
#                     '$sum': "$Hours"
#                 }
#             }
#         }
#     ]
