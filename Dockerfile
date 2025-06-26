FROM python:3.11.3-alpine

RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY . /app

WORKDIR /app

RUN python manage.py migrate