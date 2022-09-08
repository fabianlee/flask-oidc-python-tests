#
# Using the multi-stage pattern here, even though it is not necessary
# this would allow us to use a richer, non-slim base image to do the building
# then we would switch over to a lighter or slim final image
#
FROM python:3.9-slim-buster as builder

RUN mkdir /app
# copies everything from src/ into /app directory
ADD src/ /app/
# copies our personal fork of 'flask-oidc' module
ADD flask-oidc/ /app/
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

# specific user instead of root
RUN \
  useradd --create-home --shell /bin/bash app_user

# Extra python env
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
# path to python virtual env
ENV PATH "/home/app_user/venv/bin:$PATH"

# copy in Python environment and app code
COPY --from=builder /venv /home/app_user/venv
COPY --from=builder /app /home/app_user/app

RUN \
  chown -R app_user /home/app_user && \
  chmod ugo+r+w /home/app_user/venv/lib/python3.9/site-packages/certifi/cacert.pem
USER app_user

WORKDIR /home/app_user/app

EXPOSE 8081

# use python from virtualenv
#CMD [ "python", "app.py" ]
CMD [ "bash", "run.sh" ]


