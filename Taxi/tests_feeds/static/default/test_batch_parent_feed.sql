INSERT INTO services
  (id, name)
VALUES
  (1, 'service'),
  (2, 'other_service');

INSERT INTO feeds
  (feed_id, parent_feed_id, service_id, request_id, created, expire, payload, publish_at)
VALUES ('75e46d20e0d941c1af604d354dd46ca0', NULL, 1, 'my_news', '2018-12-01T00:00:00.0Z', '2019-12-01T00:00:00.0Z', '{"text": "How do you do?", "title": "Hello, Vladimir!"}', '2018-12-01T00:00:00.0Z'),
       ('38672090b4ef4a3382d064c6d9642971', NULL, 1, 'my_news', '2018-12-01T00:00:00.0Z', '2019-12-01T00:00:00.0Z', '{"text": "How do you do?", "title": "Hello, Ivan!"}', '2018-12-01T00:00:00.0Z'),
       ('57422b02229e42bdac084c589c4024c2', NULL, 2, 'my_news', '2018-12-01T00:00:00.0Z', '2019-12-01T00:00:00.0Z', '{"text": "How do you do?", "title": "Hello, Omsk!"}', '2018-12-01T00:00:00.0Z'),
       ('36f29b888314418fb8836d7400eb3c43', '75e46d20e0d941c1af604d354dd46ca0', 1, 'my_notification', '2018-12-01T01:00:00.0Z', '2019-12-01T00:00:00.0Z', '{"title": "Vladimir, you have new message"}', '2018-12-01T00:00:00.0Z'),
       ('b27edf7c10e346e681bd047a7ef5f494', '38672090b4ef4a3382d064c6d9642971', 1, 'my_notification', '2018-12-01T00:00:00.0Z', '2019-12-01T00:00:00.0Z', '{"title": "Ivan, you have new message"}', '2018-12-01T00:00:00.0Z'),
       ('0bec378a66a54d0b91c85989fcd41a85', '57422b02229e42bdac084c589c4024c2', 2, 'my_notification', '2018-12-01T00:00:00.0Z', '2019-12-01T00:00:00.0Z', '{}', '2018-12-01T00:00:00.0Z');

INSERT INTO channels
  (id, name, service_id, etag, updated)
VALUES (1, 'user:1', 1, '358af30761eb454db8af9c8f9666e5a8', '2018-12-01T00:00:01.0Z'),
       (2, 'user:2', 1, '358af30761eb454db8af9c8f9666e5a8', '2018-12-01T00:00:01.0Z'),
       (3, 'city:omsk', 2, '358af30761eb454db8af9c8f9666e5a8', '2018-12-01T00:00:01.0Z');

INSERT INTO feed_channel_status
  (feed_id, channel_id, created, status, meta)
VALUES ('75e46d20e0d941c1af604d354dd46ca0', 1, '2018-12-01T00:00:00.0Z', 'published', '{"v": 1}'),
       ('38672090b4ef4a3382d064c6d9642971', 2, '2018-12-01T00:00:00.0Z', 'published', NULL),
       ('57422b02229e42bdac084c589c4024c2', 3, '2018-12-01T00:00:00.0Z', 'published', NULL),
       ('36f29b888314418fb8836d7400eb3c43', 1, '2018-12-01T00:00:00.0Z', 'published', '{"v": 2}'),
       ('b27edf7c10e346e681bd047a7ef5f494', 2, '2018-12-01T00:00:00.0Z', 'published', NULL),
       ('0bec378a66a54d0b91c85989fcd41a85', 3, '2018-12-01T00:00:00.0Z', 'published', NULL);
