# Registration Server Design

## General

The Registeration Server (RS) runs in an infinite loop on a well known port listening for client connections. It holds the list of clients connected to it. 

Each entry in the list of clients has following information about the client : 
- hostname
- cookie 
- flag 
- TTL
- port number 
- activity in the last 30 days
- last registration date

Each entry is encapsulated as an object of class `p2p.utils.client.ClientEntry` ([link](../p2p/utils/client.py)).

## Client List

Depending on whether the list of clients should persist or not, following implementations are possible :
- in-memory list
- small file db (tinydb) : allows recovery from crash 

## Interfacing

Server runs on a well-known port given by `RegistrationServer.PORT` ([link](../p2p/rs/rs.py)). It listens for messages of type `p2p.protocol.proto.Message` ([link](../p2p/protocol/proto.py)).

### Messages

Clients who wish to communicate with the RS may do so by sending following messages :

To Register a client on the P2P network :

```
Register P2Pv1\n\n<client_nick_name>\n<port>
```

`<client_nick_name>` could be anything. `<port>` is the port on which client is running their P2P Server.

To Un-Register a client :

```
Leave P2Pv1\n\n<client_nick_name>
```

To increase TTL of a client : 

```
KeepAlive P2Pv1\n\n<client_nick_name>
```

To query peer list :

```
PQuery P2Pv1\n\n<client_nick_name>
```

### Response

The `p2p.protocol.proto.ServerResponse` ([link](../p2p/protocol/proto.py)) is of the following format :

```
RES P2Pv1\n\n<message>
```

The field `<message>` may change based on the original request message.

For `Register`, `KeepAlive`, `Leave` messages, the response contains only Success or Failure message with appropriate status code.

For `PQuery` requests, the response contains the list of peer addresses. `['127.0.0.1:9999', '127.0.0.1:3333']`
