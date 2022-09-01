FROM python:3.8.12-alpine

LABEL maintainer="https://homayoonalimohammadi.github.io"

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1

RUN apk update \
    && apk add postgresql-dev gcc python3-dev musl-dev

RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt 

COPY . .

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
