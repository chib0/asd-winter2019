FROM python:3.8

COPY . /cortex

RUN /cortex/scripts/install.sh docker

EXPOSE 8080
EXPOSE 8000
EXPOSE 5000

WORKDIR /cortex

