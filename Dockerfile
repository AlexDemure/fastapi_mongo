FROM python:3.8-slim

RUN pip install fastapi uvicorn motor pymongo pydantic openpyxl

COPY . .

EXPOSE 7040

CMD ["python", "main.py"]