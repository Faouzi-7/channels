from django.urls import path
from .consumers import FirstConsumer

websocket_urlpatterns = [
    path("firstconsumer/", FirstConsumer.as_asgi()),
]