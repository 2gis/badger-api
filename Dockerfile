FROM ubuntu:14.04

MAINTAINER Irina Shreyder <i.shreyder@2gis.ru>

RUN apt-get update
RUN apt-get install -y python3 python3-pip python3-dev python3-setuptools python-virtualenv python-tox
RUN apt-get install -y libpq-dev libcurl4-openssl-dev libsasl2-dev

ADD . /home/app/badger-api/
WORKDIR /home/app/badger-api/

RUN pip3 install -r /home/app/badger-api/requirements.txt

EXPOSE 8000
CMD ["gunicorn", "pycd.wsgi", "--config", "config.py", "-b", "0.0.0.0:8000"]