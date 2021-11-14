FROM python:slim

COPY ./requirements.txt /tmp/requirements.txt

WORKDIR /app

RUN apt-get update -qq && \
    apt-get install -y wget && \
    pip install -r /tmp/requirements.txt && \
    wget -O /app/yaml_to_table.py https://raw.githubusercontent.com/nerc-project/yaml-to-table/customized_for_nerc/yaml_to_table.py && \
    chmod ug+x /app/yaml_to_table.py
