import os

CASSANDRA_CLUSTER_HOST = os.getenv('CASSANDRA_CLUSTER_HOST', 'localhost')
CASSANDRA_CLUSTER_PORT = int(os.getenv('CASSANDRA_CLUSTER_PORT', 9042))
CASSANDRA_CLUSTER_KEYSPACE = os.getenv('CASSANDRA_CLUSTER_KEYSPACE', 'chats')

REDIS_CONNECTION_STRING = os.getenv('REDIS_CONNECTION_STRING', 'redis://localhost:6379')
