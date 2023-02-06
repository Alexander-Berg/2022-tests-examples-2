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
  ('111c69c8afe947ba887fd6404428b31c', 0, 'published/read',    '2018-12-01T00:00:00.0Z', '2019-12-01T00:00:00.0Z', '{"text": "feed1"}', '2018-12-01T00:00:00.0Z'),
  ('222c69c8afe947ba887fd6404428b31c', 0, 'published/read',    '2018-12-01T00:00:00.0Z', '2019-12-01T00:00:00.0Z', '{"text": "feed2"}', '2018-12-01T00:00:00.0Z'),
  ('333c69c8afe947ba887fd6404428b31c', 0, 'published/removed', '2018-12-01T00:00:00.0Z', '2019-12-01T00:00:00.0Z', '{"text": "feed3"}', '2018-12-01T00:00:00.0Z'),
  ('444c69c8afe947ba887fd6404428b31c', 0, 'one_channel',       '2018-12-01T00:00:00.0Z', '2019-12-01T00:00:00.0Z', '{"text": "feed4"}', '2018-12-01T00:00:00.0Z'),
  ('555c69c8afe947ba887fd6404428b31c', 0, 'viewed',            '2018-12-01T00:00:00.0Z', '2019-12-01T00:00:00.0Z', '{"text": "feed5"}', '2018-12-01T00:00:00.0Z'),
  ('666c69c8afe947ba887fd6404428b31c', 0, 'not_published',     '2018-12-01T00:00:00.0Z', '2019-12-01T00:00:00.0Z', '{"text": "feed6"}', '2018-12-10T00:00:00.0Z'),
  ('777c69c8afe947ba887fd6404428b31c', 0, 'expired',           '2018-11-01T00:00:00.0Z', '2018-11-10T00:00:00.0Z', '{"text": "feed7"}', '2018-11-01T00:00:00.0Z'),
  ('888c69c8afe947ba887fd6404428b31c', 0, 'no_expired',        '2018-11-01T00:00:00.0Z', NULL,                     '{"text": "feed7"}', '2018-11-01T00:00:00.0Z');


INSERT INTO feed_channel_status
  (feed_id, channel_id, created, status)
VALUES
  ('111c69c8afe947ba887fd6404428b31c', 1, '2018-12-01T00:00:00.0Z', 'published'),
  ('111c69c8afe947ba887fd6404428b31c', 2, '2018-12-01T00:00:00.0Z', 'published'),

  ('222c69c8afe947ba887fd6404428b31c', 1, '2018-12-01T00:00:00.0Z', 'published'),
  ('222c69c8afe947ba887fd6404428b31c', 2, '2018-12-02T00:00:00.0Z', 'read'),

  ('333c69c8afe947ba887fd6404428b31c', 1, '2018-12-01T00:00:00.0Z', 'published'),
  ('333c69c8afe947ba887fd6404428b31c', 2, '2018-12-02T00:00:00.0Z', 'removed'),

  ('444c69c8afe947ba887fd6404428b31c', 1, '2018-12-01T00:00:00.0Z', 'published'),

  ('555c69c8afe947ba887fd6404428b31c', 1, '2018-12-02T00:00:00.0Z', 'viewed'),
  ('555c69c8afe947ba887fd6404428b31c', 2, '2018-12-02T00:00:00.0Z', 'viewed'),

  ('666c69c8afe947ba887fd6404428b31c', 1, '2018-12-01T00:00:00.0Z', 'published'),
  ('666c69c8afe947ba887fd6404428b31c', 2, '2018-12-01T00:00:00.0Z', 'published'),

  ('777c69c8afe947ba887fd6404428b31c', 1, '2018-12-01T00:00:00.0Z', 'published'),
  ('777c69c8afe947ba887fd6404428b31c', 2, '2018-12-01T00:00:00.0Z', 'published'),

  ('888c69c8afe947ba887fd6404428b31c', 1, '2018-12-01T00:00:00.0Z', 'published');
