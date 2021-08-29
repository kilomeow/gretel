FROM python:3.9-bullseye

# Metadata
LABEL MAINTAINERS="dkeysil (dkeysil@protonmail.com), chimera (chimera@chimera.website)"
LABEL VERSION="1.2"

# Creating virtual enviroment
ENV VIRTUAL_ENV=/opt/venv
RUN python -m venv $VIRTUAL_ENV
# Some magic: next line also activates venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
COPY requirements.txt requirements.txt
RUN pip install --upgrade pip -r requirements.txt

# Switching to an unpriviliged user
RUN useradd --create-home gretel
USER gretel
WORKDIR /home/gretel/bot
COPY . /home/gretel/bot

# Running a bot
CMD python -u bot.py
