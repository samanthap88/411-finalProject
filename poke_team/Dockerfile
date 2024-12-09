FROM python:3.9-slim

WORKDIR /app
COPY . /app
COPY .env /app/.env

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update && apt-get install -y sqlite3

COPY . .

RUN chmod +x /app/sql/create_db.sh


VOLUME ["/app/db"]

EXPOSE 5000

CMD ["/app/entrypoint.sh"]
