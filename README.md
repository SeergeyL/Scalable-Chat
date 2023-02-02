# Scalable-Chat

Application stack:

* FastAPI
* Redis
* Cassandra
* Docker


## Application Architecture
![architecture](https://uc583fcec2add7a8da090f32d27c.previews.dropboxusercontent.com/p/thumb/ABzfENvKKPBKt_f0Labt3VLgHz64WMKnB1eLR-WOQ0kvTAaDsMo5VPjAJ91Bl7KmTzFlT-E2Gb0nVC6N2fA0SQxAsO2pX4QVDMO_ScLPrRlMkceX-7sJfORkxoQEbVdlNX8bLD8u6y62YYMaf6oCIuSGxXJEdvOEMyswuRqGIUujXk9mCB66hCHg2NZb166AEiIdAmMK_sIWMX5JMQeDosk55t_TMFZDX8SZnFlesq4zSpwaVPYr_wG9aN_ViKS93la-Th_mX9ZfGCJmxNjFOc7s1vF-K23wQTfiKb8lGBqZV4Q8zi_dQr6COo49-rf2hTCw36IFlkCtOHYZdvYkaK4Hh5whOIWJSJ4m0i1405mPzlUOGFy_urogqNnlt2yO5_GMOPmdwmf5O-Mv_UsvVX4BZKbPtorOQWVUnPNuW43qPw/p.png)

In this application Redis provides fast in-memory pub/sub for real-time communication between websockets. The lack of durability in data is compensated by Cassandra: fast, highly available and scalable storage.


## Run containers
Start the containers with default parameters or configure the project's environment variables in chat/.env.example
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


# TODO

- [ ] Add Kafka Cassandra Source Connector and Elasticseach Sink Connector
- [ ] Write api to access data from Cassandra and Elasticsearch
- [ ] Add service discovery to balance the load between websocket servers
- [ ] Cassandra driver can't be used with async/await syntax, replace with asynchronous wrapper
