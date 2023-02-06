INSERT INTO services
  (id, name)
VALUES
  (1, 'service');


INSERT INTO channels
  (id, name, service_id, etag, updated)
VALUES
  (0, 'driver:1', 1, '358af30761eb454db8af9c8f9666e5a8', '2018-12-01T00:00:01.0Z'),
  (1, 'driver:2', 1, '358af30761eb454db8af9c8f9666e5a8', '2018-12-01T00:00:01.0Z');


INSERT INTO feeds
  (feed_id, service_id, package_id, request_id, created, expire, payload, publish_at)
VALUES
  ('111c69c8afe947ba887fd6404428b31c', 1, 'p1', 'request_1', '2018-12-01T00:00:00.0Z', '2019-12-01T00:00:00.0Z', '{"text": "feed1"}', '2018-12-01T00:00:00.0Z'),
  ('222c69c8afe947ba887fd6404428b31c', 1, 'p2', 'request_2', '2018-12-01T00:00:00.0Z', '2019-12-01T00:00:00.0Z', '{"text": "feed2"}', '2018-12-02T00:00:00.0Z'),
  ('333c69c8afe947ba887fd6404428b31c', 1, 'p3', 'request_3', '2018-12-01T00:00:00.0Z', '2019-12-01T00:00:00.0Z', '{"text": "feed3"}', '2018-12-03T00:00:00.0Z');


INSERT INTO feed_channel_status
  (feed_id, channel_id, created, status, meta)
VALUES
  ('111c69c8afe947ba887fd6404428b31c', 0, '2018-12-01T00:00:00.0Z', 'published', '{}'),
  ('111c69c8afe947ba887fd6404428b31c', 1, '2018-12-02T00:00:00.0Z', 'viewed', '{"actions": ["like"]}'),
  ('222c69c8afe947ba887fd6404428b31c', 0, '2018-12-01T00:00:00.0Z', 'published', '{}'),
  ('333c69c8afe947ba887fd6404428b31c', 0, '2018-12-01T00:00:00.0Z', 'published', '{"actions": ["sad"]}'),
  ('333c69c8afe947ba887fd6404428b31c', 1, '2018-12-01T00:00:00.0Z', 'published', '{"actions": ["like", "very_good"]}');


INSERT INTO feeds_statistics
  (request_id, service_id, meta_counters, updated)
VALUES
  ('request_1', 1, '{"like": 1}', '2018-12-01T00:00:00.0Z'),
  ('request_3', 1, '{"like": 1, "sad": 1, "very_good": 1}', '2018-12-03T00:00:00.0Z');
