# Server

The `p2p.utils.server.Server` ([link](../p2p/utils/server.py)) is an abstraction over the underlying multi-client socket implemented using `select()` system call.

Any class that extends the `Server` class has the ability to launch a server using `Server.start()` method.

```python
class MyServer(Server):
    def __init__(self, host, port):
        super(MyServer, self).__init__(host=host, port=port)
```

The `Server` call has 3 callback methods to give more control over message and connected clients.

### The Reconcile Loop

This loop is an infinite loop which is triggered every 5 seconds. This method can be utilized to change the state of the server which is implementing this method.

```python
class MyServer(Server):
    ...
    def _reconcile(self):
        pass
```

## The Message Callback

Whenever the server receives a new message, it calls this method.

```python
class MyServer(Server):
    ...
    def _new_message_callback(self, conn, msg):
        """ conn : the original socket on which message was received """
        """ msg  : the original message as bytes """
        pass
```

## The Connection Callback
Whenever the server receives a new connection, it calls this method.

```python
class MyServer(Server):
    ...
    def _new_connection_callback(self, conn, msg):
        """ conn : the original socket on which message was received """
        """ msg  : the original message as bytes """
        pass
```
