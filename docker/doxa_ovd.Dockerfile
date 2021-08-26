FROM python:3.9-bullseye

# Metadata
LABEL MAINTAINERS="chimera (chimera@chimera.website)"

# Creating virtual environment
ENV VIRTUAL_ENV=/opt/venv
RUN python -m venv $VIRTUAL_ENV
# Some magic: next line also activates venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
COPY doxa_ovd/requirements.txt /tmp/requirements.txt
RUN pip install --upgrade pip -r /tmp/requirements.txt

ENV BOT_NAME="doxa_ovd"

# Switching to an unprivileged user
RUN useradd --create-home doxa_ovd
USER doxa_ovd
WORKDIR /home/doxa_ovd/bot
COPY doxa_ovd /home/doxa_ovd/bot

# Running a bot
CMD python -u main.py
