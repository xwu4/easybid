release: python manage.py migrate
web: gunicorn webapps.wsgi --log-file -
worker: python manage.py runworker channels --settings=webapps.settings -v2