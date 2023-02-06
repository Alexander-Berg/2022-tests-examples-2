CREATE TABLE qc_photo.bot_data (
    id INTEGER PRIMARY KEY,
    data JSON
);

CREATE TABLE qc_photo.chat_data (
    id BIGINT PRIMARY KEY,
    data JSON
);

CREATE TABLE qc_photo.user_data (
    id BIGINT PRIMARY KEY,
    data JSON
);

CREATE TABLE qc_photo.conversation_data (
    id SERIAL PRIMARY KEY,
    name TEXT,
    key TEXT,
    data BYTEA,

    UNIQUE (name, key)
);
