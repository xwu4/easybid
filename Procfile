web: daphne webapps.asgi:channel_layer --port $PORT --bind 0.0.0.0 -v2
chatworker: python manage.py runworker --settings=webapps.settings -v2