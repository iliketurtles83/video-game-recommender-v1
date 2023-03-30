# syntax=docker/dockerfile:1
FROM python:3.10-slim-buster

WORKDIR /app

COPY flask_app/requirements.txt /app/requirements.txt

RUN apt-get update && \
    apt-get install -y gcc

RUN pip install -r requirements.txt

COPY flask_app /app
COPY models/weighted_sim_compressed.pkl /app/models/weighted_sim_compressed.pkl
COPY data/steam_metadata_flask.csv /app/data/steam_metadata_flask.csv

CMD ["python", "app.py"]