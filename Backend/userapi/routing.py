from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # The regex captures a userid consisting of alphanumeric characters and underscores.
    # Adjust if your userids have a different format.
    re_path(r"ws/chat/(?P<userid>\w+)/$", consumers.ChatConsumer.as_asgi()),
] 