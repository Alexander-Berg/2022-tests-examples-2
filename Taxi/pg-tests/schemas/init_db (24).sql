CREATE TABLE orders (
    park_id VARCHAR(255) NOT NULL,
    id VARCHAR(255) NOT NULL,
    date_last_change TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (park_id, id)
);

CREATE TABLE feedbacks (
    park_id VARCHAR(255) NOT NULL,
    id VARCHAR(255) NOT NULL,
    date_last_change TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (park_id, id)
);

