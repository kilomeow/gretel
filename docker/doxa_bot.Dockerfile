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

# Switching to an unprivileged user
RUN useradd --create-home doxa_bot
USER doxa_bot
WORKDIR /home/doxa_bot/bot
COPY doxa_ovd /home/doxa_bot/bot

# Running a bot
CMD python -u main.py
