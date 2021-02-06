FROM python:latest

LABEL MAINTAINER="dkeysil dkeysil@protonmail.com"

WORKDIR /server
ADD ./requirements.txt /server/requirements.txt
RUN pip install -r requirements.txt
ADD . /server

CMD python -u bot.py
