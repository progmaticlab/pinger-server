FROM python:3

ADD requirements.txt /requirements.txt

RUN pip install -r /requirements.txt

ADD app /app
WORKDIR /app
