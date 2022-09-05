#
# Using the multi-stage pattern here, even though it is not necessary
# this would allow us to use a richer, non-slim base image to do the building
# then we would switch over to a lighter or slim final image
#
FROM python:3.9-slim-buster as builder

RUN mkdir /app
# copies everything from src/ into /app directory
ADD src/ /app/
WORKDIR /app

# requirements put into /app
COPY requirements.txt ./

# Sets utf-8 encoding for Python et al
ENV LANG=C.UTF-8
# Turns off writing .pyc files; superfluous on an ephemeral container.
ENV PYTHONDONTWRITEBYTECODE=1
# Seems to speed things up
ENV PYTHONUNBUFFERED=1
# Create virtual env directory
ENV VIRTUAL_ENV /venv
RUN python -m venv $VIRTUAL_ENV
# having virtualenv directory as first in PATH serves same purpose as activate
# https://pythonspeed.com/articles/activate-virtualenv-dockerfile/
ENV PATH "/venv/bin:$PATH"

# use pip from virtualenv
RUN set -ex \
  && pip install -r requirements.txt

# use python from virtualenv
CMD [ "python", "app.py" ]


#
# final image uses slim buster
# This only save 3Mb for this specific case
#
FROM python:3.9-slim-buster

# Extra python env
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
# path to python virtual env
ENV PATH "/venv/bin:$PATH"

# copy in Python environment and app code
COPY --from=builder /venv /venv
COPY --from=builder /app /app

WORKDIR /app

EXPOSE 8081

# use python from virtualenv
CMD [ "python", "app.py" ]


