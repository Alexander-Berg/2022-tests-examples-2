INSERT INTO services
  (id, name)
VALUES
  (1, 'service');


INSERT INTO channels
  (id, name, service_id, etag, updated)
VALUES
  (0, 'channel', 1, '358af30761eb454db8af9c8f9666e5a8', '2018-12-01T00:00:01.0Z');


INSERT INTO feeds
  (feed_id, service_id, payload, request_id, created, expire, publish_at)
VALUES
  ('111c69c8afe947ba887fd6404428b31c', 1, '{"text": {"key": "key1", "keyset": "client_messages"}}', 'request_1', '2018-12-01T00:00:00.0Z', '2019-12-01T00:00:00.0Z', '2018-12-04T00:00:00.0Z'),
  ('222c69c8afe947ba887fd6404428b31c', 1, '{"text": {"key": "key2", "keyset": "client_messages"}}', 'request_1', '2018-12-01T00:00:00.0Z', '2019-12-01T02:00:00.0Z', '2018-12-03T00:00:00.0Z'),
  ('333c69c8afe947ba887fd6404428b31c', 1, '{"text": {"key": "key3", "keyset": "client_messages"}}', 'request_1', '2018-12-01T00:00:00.0Z', '2019-12-01T02:00:00.0Z', '2018-12-02T00:00:00.0Z'),
  ('444c69c8afe947ba887fd6404428b31c', 1, '{"text": "ok"}',                                         'request_1', '2018-12-01T00:00:00.0Z', '2019-12-01T03:00:00.0Z', '2018-12-01T00:00:00.0Z');


INSERT INTO feed_channel_status
  (feed_id, channel_id, created, status)
VALUES
  ('111c69c8afe947ba887fd6404428b31c', 0, '2018-12-01T00:00:00.0Z', 'published'),
  ('222c69c8afe947ba887fd6404428b31c', 0, '2018-12-01T00:00:00.0Z', 'published'),
  ('333c69c8afe947ba887fd6404428b31c', 0, '2018-12-01T00:00:00.0Z', 'published'),
  ('444c69c8afe947ba887fd6404428b31c', 0, '2018-12-01T00:00:00.0Z', 'published');
