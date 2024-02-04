import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from channels.generic.websocket import AsyncWebsocketConsumer


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

    we need to have multiple instances of the same ChatConsumer be able to talk to each other. 
    Channels provides a channel layer abstraction that enables this kind of communication between consumers.

    A channel layer is a kind of communication system. It allows multiple consumer instances to talk with each other, and with other parts of Django.

    A channel layer provides the following abstractions:
        - A channel is a mailbox where messages can be sent to. Each channel has a name. 
            Anyone who has the name of a channel can send a message to the channel.
        - A group is a group of related channels. A group has a name. 
            Anyone who has the name of a group can add/remove a channel to the group by name and send a message to all channels in the group. 
            It is not possible to enumerate what channels are in a particular group.

    Every consumer instance has an automatically generated unique channel name, and so can be communicated with via a channel layer.

    In our chat application we want to have multiple instances of ChatConsumer in the same room communicate with each other. 
    To do that we will have each ChatConsumer add its channel to a group whose name is based on the room name. 
    That will allow ChatConsumers to transmit messages to all other ChatConsumers in the same room.

    Let us make sure that the channel layer can communicate with Redis. Open a Django shell and run the following commands:
        $ python3 manage.py shell
        >>> import channels.layers
        >>> channel_layer = channels.layers.get_channel_layer()
        >>> from asgiref.sync import async_to_sync
        >>> async_to_sync(channel_layer.send)('test_channel', {'type': 'hello'})
        >>> async_to_sync(channel_layer.receive)('test_channel')
        {'type': 'hello'}

    When a user posts a message, a JavaScript function will transmit the message over WebSocket to a ChatConsumer. 
    The ChatConsumer will receive that message and forward it to the group corresponding to the room name. 
    Every ChatConsumer in the same group (and thus in the same room) will then receive the message from the group 
    and forward it over WebSocket back to JavaScript, where it will be appended to the chat log.

    Several parts of the new ChatConsumer code deserve further explanation:

        self.scope["url_route"]["kwargs"]["room_name"]
            - Obtains the 'room_name' parameter from the URL route in chat/routing.py that opened the WebSocket connection to the consumer.
            - Every consumer has a scope that contains information about its connection, 
                including in particular any positional or keyword arguments from the URL route and the currently authenticated user if any.


    self.room_group_name = f"chat_{self.room_name}"
        - Constructs a Channels group name directly from the user-specified room name, without any quoting or escaping.
        - Group names may only contain alphanumerics, hyphens, underscores, or periods. Therefore this example code will fail on room names that have other characters.


    async_to_sync(self.channel_layer.group_add)(...)
        - Joins a group.
        - The async_to_sync(...) wrapper is required because ChatConsumer is a synchronous WebsocketConsumer 
            but it is calling an asynchronous channel layer method. (All channel layer methods are asynchronous.)
        - Group names are restricted to ASCII alphanumerics, hyphens, and periods only and are limited to a maximum length of 100 in the default backend. 
            Since this code constructs a group name directly from the room name, 
            it will fail if the room name contains any characters that are not valid in a group name or exceeds the length limit.


    self.accept()
        - Accepts the WebSocket connection.
        - If you do not call accept() within the connect() method then the connection will be rejected and closed. 
            You might want to reject a connection for example because the requesting user is not authorized to perform the requested action.
        - It is recommended that accept() be called as the last action in connect() if you choose to accept the connection.

    async_to_sync(self.channel_layer.group_discard)(...)
        - Leaves a group.

    async_to_sync(self.channel_layer.group_send)
        - Sends an event to a group.
        - An event has a special 'type' key corresponding to the name of the method that should be invoked on consumers that receive the event. 
            This translation is done by replacing . with _, thus in this example, chat.message calls the chat_message method.
    """

    def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name, {"type": "chat.message", "message": message}
        )

    # Receive message from room group
    def chat_message(self, event):
        message = event["message"]

        # Send message to WebSocket
        self.send(text_data=json.dumps({"message": message}))


class AsyncChatConsumer(AsyncWebsocketConsumer):
    """
    This new code is for ChatConsumer is very similar to the original code, with the following differences:
        - ChatConsumer now inherits from AsyncWebsocketConsumer rather than WebsocketConsumer.
        - All methods are async def rather than just def.
        - await is used to call asynchronous functions that perform I/O.
        - async_to_sync is no longer needed when calling methods on the channel layer.


        Even if ChatConsumer did access Django models or other synchronous code it would still be possible to rewrite it as asynchronous. 
        Utilities like asgiref.sync.sync_to_async and channels.db.database_sync_to_async can be used to call synchronous code from an asynchronous consumer. 
        The performance gains however would be less than if it only used async-native libraries.
    """
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name, {"type": "chat.message", "message": message}
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event["message"]

        # Send message to WebSocket
        await self.send(text_data=json.dumps({"message": message}))
