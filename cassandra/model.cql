CREATE KEYSPACE IF NOT EXISTS chats
    WITH REPLICATION = {'class' : 'SimpleStrategy', 'replication_factor' : '1'};


CREATE TABLE IF NOT EXISTS chats.messages_by_chat (
    chat_id UUID,
    created_at TIMESTAMP,
    user_from UUID,
    message TEXT,
    PRIMARY KEY ((chat_id), created_at)
);
