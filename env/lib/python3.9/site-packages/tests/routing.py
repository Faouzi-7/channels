
from channels import route_class
from channels.generic.websockets import WebsocketDemultiplexer
from .test_bindings import TestModelResourceBinding


application = ProtocolTypeRouter({
    # (http->django views is added by default)
    'websocket': SessionMiddlewareStack(
        URLRouter([
            path('', AsyncConsumer, name="root"),
        ])
    )
})
