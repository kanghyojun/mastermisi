FROM python:3.6.7-jessie

WORKDIR /usr/src/app

COPY requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt


COPY . /usr/src/app
CMD ./run.py prod.toml
