FROM tiangolo/uvicorn-gunicorn:python3.8

WORKDIR /app/backend

RUN pip install fastapi motor pymongo pydantic openpyxl

COPY . /app/backend

EXPOSE 7040

CMD ["python", "src/core/application.py"]