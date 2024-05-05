FROM python:3.11.4-slim-buster

EXPOSE 80
EXPOSE 443

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