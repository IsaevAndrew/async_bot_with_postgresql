# syntax=docker/dockerfile:1

FROM python:3.9-slim
ARG DEBIAN_FRONTEND=noninteractive

WORKDIR /code
RUN chown -Rh $user:$user /code
USER $user

EXPOSE 2000

COPY . /code/
COPY requirements.txt /code/

RUN apt update && apt -y install curl \
    && apt -y install python3 \
    && apt-get -y install python3-pip

RUN pip install -r requirements.txt

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1