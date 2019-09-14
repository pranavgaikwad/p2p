# Registration Server Design

The Registeration Server (RS) runs in an infinite loop on a well known port listening for client connections. It holds the list of clients connected to it. 

Each entry in the list of clients has following information about the client : 
- hostname
- cookie 
- flag 
- TTL
- port number 
- activity in the last 30 days
- last registration date

Each entry is encapsulated as an object of class Client.

```python
class Client
```

## Client List Design
Depending on whether the list of clients should persist or not, following implementations are possible :
- in-memory list
- small file db (tinydb) : allows recovery from crash 

