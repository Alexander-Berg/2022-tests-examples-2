INSERT INTO services
    (id, name)
VALUES (1, 'service');

INSERT INTO feeds
    (feed_id, service_id, request_id, created, expire, payload, publish_at)
VALUES ('75e46d20e0d941c1af604d354dd46ca0', 1, 'my_news', '2018-12-01T00:00:00.0Z', '2019-12-01T00:00:00.0Z',
        '{"text": "How do you do?", "title": "Hello, Ivan!"}', '2018-12-01T00:00:00.0Z');
