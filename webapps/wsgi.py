"""
WSGI config for webapps project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/wsgi/
"""

import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'webapps.settings'

from django.core.wsgi import get_wsgi_application
from channels.routing import get_default_application

application = get_wsgi_application()
