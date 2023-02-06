INSERT INTO services
  (id, name)
VALUES
  (0, 'service');


INSERT INTO channels
  (id, name, service_id, etag, updated)
VALUES
  (1, 'channel:1', 0, '358af30761eb454db8af9c8f9666e5a8', '2018-12-01T00:00:01.0Z'),
  (2, 'channel:2', 0, '358af30761eb454db8af9c8f9666e5a8', '2018-12-01T00:00:01.0Z');


INSERT INTO feeds
  (feed_id, service_id, request_id, created, expire, payload, publish_at)
VALUES
  ('111c69c8afe947ba887fd6404428b31c', 0, 'request', '2018-12-01T00:00:00.0Z', '2019-12-01T00:00:00.0Z', '{"text": "feed1"}', '2018-12-01T01:00:00.0Z'),
  ('222c69c8afe947ba887fd6404428b31c', 0, 'request', '2018-12-01T00:00:00.0Z', '2019-12-01T00:00:00.0Z', '{"text": "feed2"}', '2018-12-02T00:00:00.0Z'),
  ('333c69c8afe947ba887fd6404428b31c', 0, 'request', '2018-12-01T00:00:00.0Z', '2019-12-01T00:00:00.0Z', '{"text": "feed3"}', '2018-12-03T00:00:00.0Z');


INSERT INTO feed_channel_status
  (feed_id, channel_id, created, status)
VALUES
  ('111c69c8afe947ba887fd6404428b31c', 1, '2018-12-01T00:00:00.0Z', 'published'),
  ('111c69c8afe947ba887fd6404428b31c', 2, '2018-12-01T00:00:00.0Z', 'published'),

  ('222c69c8afe947ba887fd6404428b31c', 1, '2018-12-02T00:00:00.0Z', 'published'),
  ('222c69c8afe947ba887fd6404428b31c', 2, '2018-12-03T00:00:00.0Z', 'read'),

  ('333c69c8afe947ba887fd6404428b31c', 1, '2018-12-03T00:00:00.0Z', 'published'),
  ('333c69c8afe947ba887fd6404428b31c', 2, '2018-12-06T00:00:00.0Z', 'removed');
