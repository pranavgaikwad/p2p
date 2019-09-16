# Server

The `p2p.utils.server.Server` ([link](../p2p/utils/server.py)) is an abstraction over the underlying multi-client socket implemented using `select()` system call.

Any class that extends the `Server` class has the ability to launch a server using `start()` method.

```python
from p2p.utils.server import Server

class MyServer(Server):
    def __init__(self, host, port):
        super(MyServer, self).__init__(host=host, port=port)

newServer = MyServer(host='127.0.0.1', port=8888)
newServer.start() # starts the server
```

The `Server` class provides with 3 callback methods to give more control over message and connected clients.

### The Reconcile Callback

The server runs in an infinite loop calling `_reconcile()` method every 5 seconds. This is the best place to update the state of the child server.

```python
class MyServer(Server):
    ...
    def _reconcile(self):
	# update internal data structures here
        pass
```

## The Message Callback

This is triggered when the server receives a new message. Handle the new message in this method.

```python
class MyServer(Server):
    ...
    def _new_message_callback(self, conn, msg):
        """ conn : the original socket on which message was received """
        """ msg  : the original message as bytes """
	# process message here
        pass
```

## The Connection Callback
Whenever the server receives a new connection, this method is triggered.

```python
class MyServer(Server):
    ...
    def _new_connection_callback(self, conn, msg):
        """ conn : the original socket on which message was received """
        """ msg  : the original message as bytes """
        pass
```

## The Response Queue

The server holds a dictionary of Message Queues. These are the messages sent back to connected clients. A message for a particular client is indexed by the client's `conn` object. 

```python
self.messages[conn] = queue.Queue()
```

Here, `conn` represents the connected client.

Populate the queue with to send a direct message to them.

For instance, to send a new message to a client identified by `conn` :

```python
self.messages[conn].put(message.to_bytes())
```

Any message added to this queue at any point of time, will be sent to the intended client i.e. `conn`. 

The message will sent in the next available time slice.

