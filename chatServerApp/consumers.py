import json

from channels.generic.websocket import WebsocketConsumer


class ChatConsumer(WebsocketConsumer):
    """
    - Channels is a project that takes Django and extends its abilities beyond HTTP - to handle WebSockets, chat protocols, IoT protocols, and more. 
        It is built on a Python specification called ASGI.
    - Channels builds upon the native ASGI support in Django. Whilst Django still handles traditional HTTP, 
        Channels gives you the choice to handle other connections in either a synchronous or asynchronous style.

    - Channels is comprised of several packages:
        - Channels, the Django integration layer
        - Daphne, the HTTP and Websocket termination server
        - asgiref, the base ASGI library
        - channels_redis, the Redis channel layer backend (optional)

    - Channels allows you to use WebSockets and other non-HTTP protocols in your Django site. 
        For example you might want to use WebSockets to allow a page on your site to immediately receive updates 
        from your Django server without using HTTP long-polling or other expensive techniques.

    - Let us start by creating a routing configuration for Channels. 
        A Channels routing configuration is an ASGI application that is similar to a Django URLconf, 
        in that it tells Channels what code to run when an HTTP request is received by the Channels server.

    - Let us start by creating a routing configuration for Channels.
        A Channels routing configuration is an ASGI application that is similar to a Django URLconf, 
        in that it tells Channels what code to run when an HTTP request is received by the Channels server.

    NOTE:
        It is good practice to use a common path prefix like /ws/ to distinguish WebSocket connections from ordinary HTTP connections 
        because it will make deploying Channels to a production environment in certain configurations easier.

        In particular for large sites it will be possible to configure a production-grade HTTP server 
        like nginx to route requests based on path to either (1) a production-grade WSGI server 
        like Gunicorn+Django for ordinary HTTP requests or (2) a production-grade ASGI server 
        like Daphne+Channels for WebSocket requests.

        Note that for smaller sites you can use a simpler deployment strategy where Daphne serves all requests 
            - HTTP and WebSocket - rather than having a separate WSGI server. 
        In this deployment configuration no common path prefix like /ws/ is necessary.


    This is a synchronous WebSocket consumer that accepts all connections, receives messages from its client, 
    and echos those messages back to the same client. 
    Channels also supports writing asynchronous consumers for greater performance. 
    However any asynchronous consumer must be careful to avoid directly performing blocking operations, 
    such as accessing a Django model.

    ASGI.py:
        This root routing configuration specifies that when a connection is made to the Channels development server, 
        the ProtocolTypeRouter will first inspect the type of connection. If it is a WebSocket connection (ws:// or wss://), 
        the connection will be given to the AuthMiddlewareStack.

        The AuthMiddlewareStack will populate the connections scope with a reference to the currently authenticated user, 
        similar to how Django AuthenticationMiddleware populates the request object of a view function with the currently authenticated user. 
        (Scopes will be discussed later in this tutorial.) Then the connection will be given to the URLRouter.

        The URLRouter will examine the HTTP path of the connection to route it to a particular consumer, 
        based on the provided url patterns.
    """

    def connect(self):
        self.accept()

    def disconnect(self, code):
        return super().disconnect(code)

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        self.send(text_data=json.dumps({"message": message}))
