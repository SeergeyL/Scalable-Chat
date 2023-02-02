# Scalable-Chat

Application stack:

* FastAPI
* Redis
* Cassandra
* Docker


## Application Architecture
![architecture](https://www.dropbox.com/s/itx3u8m2gerarc3/architecture.png?dl=0)

In this application Redis provides fast in-memory pub/sub for real-time communication between websockets. The lack of durability in data is compensated by Cassandra: fast, highly available and scalable storage.


## Run containers
Start the containers
```
docker-compose up -d
```
Wait untill all of them are running smoothly and create model in cassandra
```
make create-models
```

After that any application can connect to the server via websocket connection
```javascript
let ws = new WebSocket('ws://localhost:8000/ws/chat/{chat_id}/?token={token}')
```

Message sent to the websocket follows the model below:
```python
class ChatMessage(BaseModel):
    event: str
    message: str
```
Where event represents one of the following

|    **event**    |               **description**              |
|:---------------:|:------------------------------------------:|
| message:message | New message was sent to the websocket      |
| message:edit    | Message update event sent to the websocket |
| message:delete  | Message delete event sent to the websocket |
