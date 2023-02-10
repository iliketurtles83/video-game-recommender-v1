# syntax=docker/dockerfile:1
FROM python:3.10-slim-buster

WORKDIR /app

COPY flask_app/requirements.txt /app

RUN apt-get update && \
    apt-get install -y gcc

RUN pip install -r requirements.txt

COPY flask_app /app
COPY models/weighted_sim.pkl /models/weighted_sim.pkl
COPY data/steam_app_metadata_clean.csv /data/steam_app_metadata_clean.csv

CMD ["python", "app.py"]