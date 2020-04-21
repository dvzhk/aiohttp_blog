FROM python:3.6


WORKDIR /app

ADD . /app

RUN ls

RUN pip3 install -r requirements.txt

EXPOSE 8000
