FROM python:slim

WORKDIR /app

COPY ./requirements.txt /tmp/requirements.txt

RUN pip install -r /tmp/requirements.txt

COPY ./yaml_to_table.py /app/yaml_to_table.py
