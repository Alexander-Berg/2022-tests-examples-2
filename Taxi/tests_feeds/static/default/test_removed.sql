INSERT INTO services
  (id, name)
VALUES
  (123, 'test_removed');


INSERT INTO channels
  (id, name, service_id, etag, updated)
VALUES
  (0, 'city:moscow', 123, '358af30761eb454db8af9c8f9666e5a8', '2018-12-01T00:00:01.0Z'),
  (1, 'user:111111', 123, '358af30761eb454db8af9c8f9666e5a8', '2018-12-01T00:00:01.0Z');


INSERT INTO feeds
  (feed_id, service_id, package_id, request_id, created, expire, payload, publish_at)
VALUES
  ('111c69c8afe947ba887fd6404428b31c', 123, 'p1', 'request_1', '2018-12-01T00:00:00.0Z', '2019-12-01T00:00:00.0Z', '{}', '2018-12-01T00:00:00.0Z'),
  ('222c69c8afe947ba887fd6404428b31c', 123, 'p1', 'request_1', '2018-12-01T00:00:00.0Z', '2019-12-01T00:00:00.0Z', '{}', '2018-12-01T00:00:00.0Z'),
  ('333c69c8afe947ba887fd6404428b31c', 123, 'p1', 'request_1', '2018-12-01T00:00:00.0Z', '2019-12-01T00:00:00.0Z', '{}', '2018-12-01T00:00:00.0Z');


INSERT INTO feed_channel_status
  (feed_id, channel_id, created, status)
VALUES
  ('111c69c8afe947ba887fd6404428b31c', 0, '2018-12-01T00:00:00.0Z', 'published'),
  ('111c69c8afe947ba887fd6404428b31c', 1, '2018-12-01T00:00:00.0Z', 'removed'),

  ('222c69c8afe947ba887fd6404428b31c', 0, '2018-12-01T00:00:00.0Z', 'removed'),
  ('222c69c8afe947ba887fd6404428b31c', 1, '2018-12-01T00:00:00.0Z', 'published'),

  ('333c69c8afe947ba887fd6404428b31c', 0, '2018-12-01T00:00:00.0Z', 'published'),
  ('333c69c8afe947ba887fd6404428b31c', 1, '2018-12-01T00:00:00.0Z', 'published');
