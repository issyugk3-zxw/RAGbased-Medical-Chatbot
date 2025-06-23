"""
ASGI config for mcbotBackend project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
import django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
# Ensure this import path is correct based on your project structure
# If userapi.routing doesn't exist yet, this will be a problem until it's created.
import userapi.routing

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mcbotBackend.settings")
django.setup() # Explicitly setup Django

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket":  URLRouter(userapi.routing.websocket_urlpatterns),
    }
)
