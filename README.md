[![Build Status](https://travis-ci.org/2gis/badger-api.svg?branch=master)](https://travis-ci.org/2gis/badger-api)

# Badger-api
Badger-api is an open source backend service (REST API) for [Badger] (https://github.com/2gis/badger) (AngularJS web UI).

# Installation

### Development version

Install dependencies:
```bash
   apt-get install -y python python-dev python-pip python-setuptools python-virtualenv python-tox
   apt-get install -y libpq-dev libcurl4-openssl-dev libsasl2-dev
```

Clone repository:
```bash
   git clone https://github.com/2gis/badger-api.git
   cd badger-api
```

Install [Vagrant] (https://www.vagrantup.com/) and type:
```bash
   vagrant up
```
*Vagrant will start two Docker containers with postgresql and rabbitmq.*

Install dev requirements and run tests:
```bash
   tox
```

Activate virtual env:
```bash
   source .tox/py34/bin/activate
```

Run api + celery:
```bash
   honcho start -f Procfile.dev
```

Now your api is available at http://localhost:8000/api/


# Usage

To start adding content to api, you need a user. Run following command to create it:
```bash
   honcho run ./manage.py createsuperuser
```

The Django admin site is available at http://localhost:8000/admin/

### Secret key

For production usage you need secret key. Don't forget to [generate it] (https://gist.github.com/mattseymour/9205591) and add to .env

