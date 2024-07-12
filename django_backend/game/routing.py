from django.urls import path, re_path
from . import consumers_4pl
from . import consumers_2pl

# equivalent to the url patterns in the urls.py file for websockets
websocket_urlpatterns = [
    path('ws/pong/', consumers_2pl.PongConsumer.as_asgi()),
	path('ws/4pong/', consumers_4pl.PongConsumer.as_asgi()),
    #re_path(r'ws/game/(?P<session_id>\w+)/$', consumers_2pl.PongConsumer.as_asgi()),
    re_path(r'ws/game/(?P<session_id>[0-9a-fA-F-]+)/$', consumers_2pl.PongConsumer.as_asgi()),
]
