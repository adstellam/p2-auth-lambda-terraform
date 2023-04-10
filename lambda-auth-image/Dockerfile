# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster

WORKDIR /app
COPY ./*.py .

RUN pip3 install pipenv
RUN pipenv install cognitojwt[sync]

CMD ["pipenv", "run", "python3", "index.py"]

