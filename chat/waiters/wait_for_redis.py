import os

from redis import Redis
from waiters.backoff import backoff


@backoff()
def wait_for_redis():
    conn_string = os.getenv('REDIS_CONNECTION_STRING', 'redis://localhost:6379')
    redis = Redis.from_url(conn_string)
    print('Ping redis')
    redis.ping()
