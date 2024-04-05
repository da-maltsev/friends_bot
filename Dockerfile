ARG PYTHON_VERSION

#
# Build poetry and export compiled dependecines as plain requirements.txt
#
FROM python:${PYTHON_VERSION}-slim-bookworm as deps-compile

WORKDIR /
COPY poetry.lock pyproject.toml /

# Version is taken from poetry.lock, assuming it is generated with up-to-date version of poetry
RUN pip install --no-cache-dir poetry==$(cat poetry.lock |head -n1|awk -v FS='(Poetry |and)' '{print $2}')
RUN poetry export --format=requirements.txt > requirements.txt


#
# Base image
#
FROM python:${PYTHON_VERSION}-slim-bookworm as base
LABEL maintainer="danil.zlatoust9999@gmail.com"

RUN apt-get update \
  && apt-get --no-install-recommends install -y gettext locales-all tzdata git wait-for-it wget \
  && rm -rf /var/lib/apt/lists/*

COPY --from=deps-compile /requirements.txt /
RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /src
COPY src /src

USER nobody

CMD python main.py