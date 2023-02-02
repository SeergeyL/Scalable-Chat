import os

from cassandra.cluster import Cluster
from waiters.backoff import backoff


@backoff()
def wait_for_cassandra():
    host = os.getenv('CASSANDRA_CLUSTER_HOST', 'localhost')
    port = int(os.getenv('CASSANDRA_CLUSTER_PORT', 9042))
    keyspace = os.getenv('CASSANDRA_CLUSTER_KEYSPACE', 'chats')

    print('Ping cassandra')
    cluster = Cluster([host], port=port)
    cluster.connect(keyspace)
