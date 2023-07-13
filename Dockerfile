FROM python:3.11

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE qaas.settings

RUN mkdir -p /code
WORKDIR /code

COPY . /code/
RUN pip3 install poetry
RUN poetry config virtualenvs.create false
RUN poetry install -n --no-ansi
