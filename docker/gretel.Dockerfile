FROM python:3.9-alpine

# Metadata
LABEL MAINTAINERS="chimera (chimera@chimera.website)"

# Installing apps
RUN apk add build-base libffi-dev

# Creating virtual environment
ENV VIRTUAL_ENV=/opt/venv
RUN python -m venv $VIRTUAL_ENV
# Some magic: next line also activates venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
COPY requirements.txt /tmp/requirements.txt
RUN pip install --upgrade pip -r /tmp/requirements.txt

# Switching to an unprivileged user
RUN adduser --home /home/gretel/ --disabled-password gretel
USER gretel
WORKDIR /home/gretel/bot
COPY . /home/gretel/bot

# Running a bot
CMD python -u bot.py
