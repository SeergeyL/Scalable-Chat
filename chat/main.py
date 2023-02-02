import asyncio
import datetime
import json
import uuid

import aioredis
import config
import uvicorn
from cassandra.cluster import EXEC_PROFILE_DEFAULT, Cluster, ExecutionProfile
from cassandra.policies import ConsistencyLevel, RoundRobinPolicy
from cassandra.query import dict_factory
from fastapi import (Depends, FastAPI, HTTPException, WebSocket,
                     WebSocketDisconnect, WebSocketException, status)
from pydantic import BaseModel, ValidationError

app = FastAPI()
redis: aioredis.Redis = None
cassandra_cluster = None
cassandra_session = None


class ChatMessage(BaseModel):
    event: str
    message: str


class ChatMessageExtended(ChatMessage):
    chat_id: uuid.UUID
    created_at: datetime.datetime
    user_from: uuid.UUID


def save_message_to_cassandra(message: ChatMessageExtended):
    """
    Saves message to cassandra table.
    """
    query = """
        INSERT INTO messages_by_chat (chat_id, created_at, user_from, message)
        VALUES (%(chat_id)s, %(created_at)s, %(user_from)s, %(message)s)
    """
    cassandra_session.execute(query, message.dict())


async def chat_consumer(ws: WebSocket, chat_id: uuid.UUID):
    """
    Function is responsible for getting messages from message broker
    and sending them to the client via websocket conection.
    """
    channel = redis.pubsub()
    await channel.subscribe(str(chat_id))

    while True:
        message = await channel.get_message(ignore_subscribe_messages=True)
        if not message or not message['data'].strip():
            continue
        message = json.loads(message['data'])
        try:
            await ws.send_json(message)
        except RuntimeError:
            # Sending message to closed socket raises RuntimeError
            # not WebSocketDisconnect
            break
    await channel.close()


async def chat_producer(ws: WebSocket, chat_id: uuid.UUID, user_id: uuid.UUID):
    """
    Function is responsible for getting messages from user 
    via websocket connection and sending them to the message broker.

    Before sending message to the broker they are saved to cassandra.
    """
    while True:
        try:
            message = await ws.receive_json()
            message = ChatMessage(
                event=message['event'],
                message=message['message']
            )
        except WebSocketDisconnect:
            break

        except ValidationError:
            raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)

        message = ChatMessageExtended(
            **message.dict(),
            chat_id=chat_id,
            user_from=user_id,
            created_at=datetime.datetime.now()
        )
        save_message_to_cassandra(message)
        await redis.publish(str(chat_id), message.json())


def get_user_by_token(token: str) -> uuid.UUID:
    """
    Fake function which imitates user authentication by token.

    Should be replaced afterwards to user authentication
    by external service
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return uuid.uuid4()


@app.websocket("/chat/{chat_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    chat_id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_user_by_token)
):
    """
    Main function to handle user websocket connection,
    which creates on each connection two handlers
    for scalable communication between websockets
    """
    await websocket.accept()

    consumer = asyncio.create_task(chat_consumer(websocket, chat_id))
    producer = asyncio.create_task(chat_producer(websocket, chat_id, user_id))

    await consumer
    await producer


@app.on_event("startup")
async def startup():
    global redis, cassandra_cluster, cassandra_session

    # Wait for external services to be in running state
    from waiters import wait_for_cassandra, wait_for_redis
    wait_for_redis.wait_for_redis()
    wait_for_cassandra.wait_for_cassandra()

    # Setup Redis
    pool = aioredis.ConnectionPool.from_url(
        config.REDIS_CONNECTION_STRING,
        max_connections=128
    )
    redis = aioredis.Redis(connection_pool=pool)

    # Setup Cassandra
    profile = ExecutionProfile(
        load_balancing_policy=RoundRobinPolicy(),
        consistency_level=ConsistencyLevel.QUORUM,
        row_factory=dict_factory
    )
    cassandra_cluster = Cluster(
        [config.CASSANDRA_CLUSTER_HOST],
        port=config.CASSANDRA_CLUSTER_PORT,
        execution_profiles={EXEC_PROFILE_DEFAULT: profile},
    )
    cassandra_session = cassandra_cluster.connect(
        config.CASSANDRA_CLUSTER_KEYSPACE
    )


@app.on_event("shutdown")
async def shutdown():
    await redis.close()
    cassandra_session.close()
    cassandra_cluster.close()


if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        port=8000,
        reload=True
    )
