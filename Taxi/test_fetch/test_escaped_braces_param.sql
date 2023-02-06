INSERT INTO services
  (id, name)
VALUES
  (1, 'service');

INSERT INTO feeds
  (feed_id, service_id, request_id, created, expire, payload, publish_at)
VALUES ('75e46d20e0d941c1af604d354dd46ca0', 1, 'my_news', '2018-12-01T00:00:00.0Z', '2022-12-01T00:00:00.0Z', '{"text": "Happy new {year} year!"}', '2018-12-01T00:00:00.0Z'),
       ('38672090b4ef4a3382d064c6d9642971', 1, 'my_news', '2018-12-01T00:00:00.0Z', '2022-12-01T00:00:00.0Z', '{"text": "Hello, {name}! Happy new \\{year\\} year! \\{smile\\}"}', '2018-12-01T01:00:00.0Z');

INSERT INTO channels
  (id, name, service_id, etag, updated)
VALUES (1, 'user:1', 1, '358af30761eb454db8af9c8f9666e5a8', '2018-12-01T00:00:01.0Z'),
       (2, 'user:2', 1, '358af30761eb454db8af9c8f9666e5a8', '2018-12-01T00:00:01.0Z');

INSERT INTO feed_channel_status
  (feed_id, channel_id, created, status, meta)
VALUES ('75e46d20e0d941c1af604d354dd46ca0', 1, '2018-12-01T00:00:00.0Z', 'published', NULL),
       ('38672090b4ef4a3382d064c6d9642971', 2, '2018-12-01T00:00:00.0Z', 'published', NULL);

INSERT INTO feed_payload
(feed_id, channel_id, payload_overrides, payload_params)
VALUES ('38672090b4ef4a3382d064c6d9642971', 2, NULL, '{"(name, Ivan)"}');
