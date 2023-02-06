INSERT INTO services
(id, name)
VALUES
    (1, 'service');


INSERT INTO feeds
    (feed_id, parent_feed_id, service_id, request_id, created, expire, payload, publish_at)
VALUES
    ('36f29b888314418fb8836d7400eb3c43', NULL, 1, 'my_notification_1', '2018-12-01T00:00:00.0Z', '2018-12-01T00:00:00.0Z', '{"title": "Vladimir, you have new message"}', '2018-12-01T00:00:00.0Z'),
    ('b27edf7c10e346e681bd047a7ef5f494', NULL, 1, 'my_notification_2', '2018-12-01T00:00:00.0Z', '2018-12-01T00:00:00.0Z', '{"title": "Ivan, you have new message"}', '2018-12-01T00:00:00.0Z'),
    ('dfd998fbf1b14b20ac2e5abaf48ba386', NULL, 1, 'my_notification_3', '2018-12-01T00:00:00.0Z', '2018-12-01T00:00:00.0Z', '{"title": "Hello, {city}"}', '2018-12-01T00:00:00.0Z'),
    ('22d998fbf1b14b20ac2e5abaf48ba386', 'dfd998fbf1b14b20ac2e5abaf48ba386', 1, 'parent', '2018-12-01T00:00:00.0Z', '2018-12-01T00:00:00.0Z', '{"title": "Hello, {city}"}', '2018-12-01T00:00:00.0Z');


INSERT INTO channels
    (id, name, service_id, etag, updated)
VALUES
    (1, 'user:1', 1, '358af30761eb454db8af9c8f9666e5a8', '2018-12-01T00:00:01.0Z'),
    (2, 'user:2', 1, '358af30761eb454db8af9c8f9666e5a8', '2018-12-01T00:00:01.0Z');


INSERT INTO feed_channel_status
    (feed_id, channel_id, created, status)
VALUES
    ('36f29b888314418fb8836d7400eb3c43', 1, '2018-12-01T00:00:00.0Z', 'published'),
    ('b27edf7c10e346e681bd047a7ef5f494', 2, '2018-12-01T00:00:00.0Z', 'published'),
    ('dfd998fbf1b14b20ac2e5abaf48ba386', 2, '2018-12-01T00:00:00.0Z', 'published'),
    ('dfd998fbf1b14b20ac2e5abaf48ba386', 1, '2018-12-01T00:00:00.0Z', 'published'),
    ('22d998fbf1b14b20ac2e5abaf48ba386', 1, '2018-12-01T00:00:00.0Z', 'published');


INSERT INTO feed_payload
    (feed_id, channel_id, payload_overrides, payload_params)
VALUES
    ('36f29b888314418fb8836d7400eb3c43', 1, '{"alert": true}', NULL),
    ('b27edf7c10e346e681bd047a7ef5f494', 2, NULL, NULL),
    ('dfd998fbf1b14b20ac2e5abaf48ba386', 1, NULL, '{"(city, Omsk)"}'),
    ('dfd998fbf1b14b20ac2e5abaf48ba386', 2, NULL, '{"(city, Msk)"}'),
    ('22d998fbf1b14b20ac2e5abaf48ba386', 1, NULL, '{"(city, Omsk)"}');


INSERT INTO remove_requests_by_request_id
    (service_id, request_id, max_created, recursive, created)
VALUES
    (1, 'my_notification_1', '2018-12-02T00:00:00.0Z', false, '2018-12-02T00:00:00.0Z'),
    (1, 'my_notification_2', '2018-12-02T01:00:00.0Z', false, '2018-12-02T01:00:00.0Z'),
    (1, 'my_notification_3', '2018-12-02T02:00:00.0Z', false, '2018-12-02T02:00:00.0Z');
