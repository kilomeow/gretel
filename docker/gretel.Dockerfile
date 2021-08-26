FROM python:3.9-bullseye

# Metadata
LABEL MAINTAINERS="dkeysil (dkeysil@protonmail.com), chimera (chimera@chimera.website)"
LABEL VERSION="1.3"

# Creating virtual environment
ENV VIRTUAL_ENV=/opt/venv
RUN python -m venv $VIRTUAL_ENV
# Some magic: next line also activates venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
COPY gretel/requirements.txt /tmp/requirements.txt
RUN pip install --upgrade pip -r /tmp/requirements.txt

# Switching to an unprivileged user
RUN useradd --create-home gretel
USER gretel
WORKDIR /home/gretel/bot
COPY gretel /home/gretel/bot

# Running a bot
CMD python -u bot.py
