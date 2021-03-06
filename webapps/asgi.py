"""
ASGI config for webapps project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/asgi/
"""

import os

# from channels.auth import AuthMiddlewareStack
from channels.routing import get_default_application
import chat.routing



# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webapps.settings')

# application = ProtocolTypeRouter({
#     "http": get_default_application(),
#     "websocket": AuthMiddlewareStack(
#         URLRouter(
#             chat.routing.websocket_urlpatterns
#         )
#     ),
# })

os.environ['DJANGO_SETTINGS_MODULE'] = 'webapps.settings'
import django
django.setup()
application = get_default_application()