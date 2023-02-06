INSERT INTO services
  (id, name)
VALUES (10, 'tariffeditor');

INSERT INTO feeds
  (feed_id, service_id, request_id, created, expire, payload, publish_at)
VALUES ('11111111111111111111111111111111', 10, 'not_delayed', '2018-12-01T00:00:00.0Z', '2018-12-11T00:00:00.0Z', '{}', '2018-12-01T00:00:00.0Z'),
       ('22222222222222222222222222222222', 10, 'delayed',     '2018-12-01T00:00:00.0Z', '2018-12-11T00:00:00.0Z', '{}', '2018-12-02T00:00:00.0Z');

INSERT INTO channels
  (id, name, service_id, etag, updated)
VALUES (0, 'channel0:not_updated', 10, '358af30761eb454db8af9c8f9666e5a8', '2018-12-01T00:00:00.0Z'),
       (1, 'channel1:tobe_updated', 10, '358af30761eb454db8af9c8f9666e5a8', '2018-12-01T00:00:00.0Z'),
       (2, 'channel2:tobe_updated', 10, '358af30761eb454db8af9c8f9666e5a8', '2018-12-01T00:00:00.0Z');

INSERT INTO feed_channel_status
  (feed_id, channel_id, created, status)
VALUES ('11111111111111111111111111111111', 0, '2018-12-01T00:00:00.0Z', 'published'),
       ('22222222222222222222222222222222', 1, '2018-12-01T00:00:00.0Z', 'published'),
       ('22222222222222222222222222222222', 2, '2018-12-01T00:00:00.0Z', 'published');
