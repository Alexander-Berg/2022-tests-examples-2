INSERT INTO services
  (id, name)
VALUES
  (1, 'service'),
  (2, 'other_service');


INSERT INTO channels
  (id, name, service_id, etag, updated)
VALUES
  (0, 'city:moscow', 1, '358af30761eb454db8af9c8f9666e5a8', '2018-12-01T00:00:01.0Z'),
  (1, 'driver:1', 1, '358af30761eb454db8af9c8f9666e5a8', '2018-12-01T00:00:01.0Z'),
  (2, 'channel:1', 2, '358af30761eb454db8af9c8f9666e5a8', '2018-12-01T00:00:01.0Z'),
  (3, 'channel:2', 2, '358af30761eb454db8af9c8f9666e5a8', '2018-12-01T00:00:01.0Z');


INSERT INTO feeds
  (feed_id, service_id, request_id, created, expire, payload, publish_at)
VALUES
  ('111c69c8afe947ba887fd6404428b31c', 1, 'request_1',     '2018-12-01T00:00:00.0Z', '2019-12-01T00:00:00.0Z', '{"text": "feed1"}', '2018-12-01T00:00:00.0Z'),
  ('222c69c8afe947ba887fd6404428b31c', 1, 'request_1',     '2018-12-01T00:00:00.0Z', '2019-12-01T00:00:00.0Z', '{"text": "feed2"}', '2018-12-01T00:00:00.0Z'),
  ('333c69c8afe947ba887fd6404428b31c', 1, 'request_1',     '2018-12-01T00:00:00.0Z', '2019-12-01T00:00:00.0Z', '{"text": "feed3"}', '2018-12-02T00:00:00.0Z'),
  ('444c69c8afe947ba887fd6404428b31c', 2, 'request_2',     '2018-12-01T00:00:00.0Z', '2019-12-01T00:00:00.0Z', '{"text": "feed4"}', '2018-12-02T00:00:00.0Z'),
  ('555c69c8afe947ba887fd6404428b31c', 1, 'not_published', '2018-12-01T00:00:00.0Z', '2019-12-01T00:00:00.0Z', '{"text": "feed4"}', '2019-01-02T00:00:00.0Z'),
  ('666c69c8afe947ba887fd6404428b31c', 1, 'expire', '2018-12-01T00:00:00.0Z', '2019-01-01T00:00:00.0Z', '{"text": "feed4"}', '2018-12-02T00:00:00.0Z');


INSERT INTO feed_channel_status
  (feed_id, channel_id, created, status, meta)
VALUES
  ('111c69c8afe947ba887fd6404428b31c', 0, '2018-12-01T00:00:00.0Z', 'published', '{"info": "feed1 for moscow"}'),
  ('111c69c8afe947ba887fd6404428b31c', 1, '2018-12-02T00:00:00.0Z', 'removed', '{"info": "feed1 removed for driver:1"}'),

  ('222c69c8afe947ba887fd6404428b31c', 0, '2018-12-01T00:00:00.0Z', 'read', '{"info": "feed2 for moscow"}'),
  ('222c69c8afe947ba887fd6404428b31c', 1, '2018-12-02T00:00:00.0Z', 'published', '{"info": "feed2 for driver:1"}'),

  ('333c69c8afe947ba887fd6404428b31c', 0, '2018-12-01T00:00:00.0Z', 'read', '{}'),
  ('333c69c8afe947ba887fd6404428b31c', 1, '2018-12-02T00:00:00.0Z', 'published', '{}'),

  ('444c69c8afe947ba887fd6404428b31c', 2, '2018-12-01T00:00:00.0Z', 'read', '{}'),
  ('444c69c8afe947ba887fd6404428b31c', 3, '2018-12-02T00:00:00.0Z', 'published', '{}'),

  ('555c69c8afe947ba887fd6404428b31c', 0, '2018-12-01T00:00:00.0Z', 'published', '{}');
