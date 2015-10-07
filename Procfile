cmd: gunicorn pycd.wsgi --config config.py -b 0.0.0.0:5000
beat: python manage.py celery beat -S djcelery.schedulers.DatabaseScheduler
