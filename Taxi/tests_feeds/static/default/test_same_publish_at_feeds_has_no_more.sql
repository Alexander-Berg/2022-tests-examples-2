INSERT INTO services
  (id, name)
VALUES
  (1, 'service');


INSERT INTO channels
  (id, name, service_id, etag, updated)
VALUES
  (0, 'city:moscow;position:director', 1, '358af30761eb454db8af9c8f9666e5a8', '2018-12-01T00:00:01.0Z');


INSERT INTO feeds
  (feed_id, service_id, request_id, created, expire, payload, publish_at)
VALUES
  ('111c69c8afe947ba887fd6404428b31c', 1, 'request_1', '2018-12-01T00:00:00.0Z', '2020-12-01T00:00:00.0Z', '{"text": "feed1"}', '2018-12-01T12:00:00.0Z'),
  ('222c69c8afe947ba887fd6404428b31c', 1, 'request_1', '2018-12-01T00:00:00.0Z', '2020-12-01T00:00:00.0Z', '{"text": "feed2"}', '2018-12-01T12:00:00.0Z'),
  ('333c69c8afe947ba887fd6404428b31c', 1, 'request_1', '2018-12-01T00:00:00.0Z', '2020-12-01T00:00:00.0Z', '{"text": "feed3"}', '2018-12-02T00:00:00.0Z'),
  ('444c69c8afe947ba887fd6404428b31c', 1, 'request_1', '2018-12-01T00:00:00.0Z', '2020-12-01T00:00:00.0Z', '{"text": "feed4"}', '2018-12-02T00:00:00.0Z');


INSERT INTO feed_channel_status
  (feed_id, channel_id, created, status)
VALUES
  ('111c69c8afe947ba887fd6404428b31c', 0, '2018-12-10T00:00:00.0Z', 'published'),
  ('222c69c8afe947ba887fd6404428b31c', 0, '2018-12-10T00:00:00.0Z', 'read'),
  ('333c69c8afe947ba887fd6404428b31c', 0, '2018-12-10T00:00:00.0Z', 'read'),
  ('444c69c8afe947ba887fd6404428b31c', 0, '2018-12-10T00:00:00.0Z', 'published');
