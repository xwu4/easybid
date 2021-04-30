web: gunicorn webapps.wsgi
web2: daphne webapps.asgi:application --port $PORT --bind 0.0.0.0 -v2
worker: python manage.py runworker channels --settings=webapps.settings -v2