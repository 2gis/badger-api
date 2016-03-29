web: gunicorn pycd.wsgi --config config.py -b 0.0.0.0:$PORT
#beat: python manage.py celery beat -S djcelery.schedulers.DatabaseScheduler
worker: python manage.py celery worker -Q default -l DEBUG
