# syntax=docker/dockerfile:1
FROM python:3.10-slim-buster

WORKDIR /app

RUN apt-get update && \
    apt-get install -y gcc

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY flask_app/requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt


COPY ./flask_app /app
COPY ./models/weighted_sim_compressed.pkl /app/utils/weighted_sim_compressed.pkl
COPY ./data/steam_metadata_flask.csv /app/utils/steam_metadata_flask.csv

CMD ["python", "app.py"]