FROM python:3.11.4-slim-buster

EXPOSE 8000

ENV PYTHONUNBUFFERED 1

WORKDIR app/

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

RUN adduser \
    --disabled-password \
    --no-create-home \
    hackathon-bot-user

USER hackathon-bot-user