# Badger-api [![Build Status](https://travis-ci.org/2gis/badger-api.svg?branch=master)](https://travis-ci.org/2gis/badger-api) [![Coverage Status](https://coveralls.io/repos/2gis/badger-api/badge.svg?branch=master&service=github)](https://coveralls.io/github/2gis/badger-api?branch=master)
Badger-api is an open source backend service (REST API) for [Badger] (https://github.com/2gis/badger) (AngularJS web UI).

# Installation

### <a href="README.md">Development version</a> | Deploy to Heroku

Clone repository:
```bash
git clone https://github.com/2gis/badger-api.git
cd badger-api
```

Create an app on Heroku:
```bash
heroku create appname
```

Install CloudAMQP add-on:
```bash
heroku addons:create cloudamqp
```

Configure you app:
```bash
heroku config | grep CLOUDAMQP_URL
heroku config:set BROKER_URL=amqp://user:pass@ec2.clustername.cloudamqp.com/vhost
heroku config:set CDWS_API_HOSTNAME=appname.herokuapp.com
```

Sync database:
```bash
heroku run python manage.py syncdb
```

Copy worker process from Procfile.dev to Procfile:
```bash
worker: python manage.py celery worker -O fair -l DEBUG
```

Save your changes:
```bash
git add .
git commit -m "save my changes"
```

Deploy app:
```bash
git push heroku master
```

Start processes:
```bash
heroku ps:scale worker=1 beat=1 web=1
```


