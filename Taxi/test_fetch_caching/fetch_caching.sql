INSERT INTO services
  (id, name)
VALUES
  (100, 'caching_service');


INSERT INTO channels
  (id, name, service_id, etag, updated)
VALUES
  (0, 'city:moscow', 100, '358af30761eb454db8af9c8f9666e5a8', '2018-12-01T00:00:01.0Z'),
  (1, 'user:111111', 100, '358af30761eb454db8af9c8f9666e5a8', '2018-12-01T00:00:01.0Z');


INSERT INTO feeds
  (feed_id, service_id, package_id, request_id, created, expire, payload, publish_at)
VALUES
  ('111c69c8afe947ba887fd6404428b31c', 100, 'p1', 'request_1', '2018-12-01T00:00:00.0Z', '2019-12-01T00:00:00.0Z', '{"data": 1}', '2018-12-01T00:00:00.0Z'),
  ('222c69c8afe947ba887fd6404428b31c', 100, 'p2', 'request_2', '2018-12-01T00:00:00.0Z', '2019-12-01T00:00:00.0Z', '{"data": 2}', '2018-12-02T00:00:00.0Z'),
  ('333c69c8afe947ba887fd6404428b31c', 100, 'p3', 'request_3', '2018-12-01T00:00:00.0Z', '2019-12-01T00:00:00.0Z', '{"data": 3}', '2018-12-03T00:00:00.0Z'),
  ('444c69c8afe947ba887fd6404428b31c', 100, 'p4', 'request_4', '2018-12-01T00:00:00.0Z', '2019-12-01T00:00:00.0Z', '{"data": "{number}"}', '2018-12-04T00:00:00.0Z'),
  ('555c69c8afe947ba887fd6404428b31c', 100, 'p5', 'request_5', '2018-12-01T00:00:00.0Z', '2019-12-01T00:00:00.0Z', '{"data": 5}', '2018-12-05T00:00:00.0Z'),
  ('666c69c8afe947ba887fd6404428b31c', 100, 'p6', 'too_early', '2018-12-01T00:00:00.0Z', '2019-12-01T00:00:00.0Z', '{"data": 6}', '2018-12-20T00:00:00.0Z'),
  ('777c69c8afe947ba887fd6404428b31c', 100, 'p7', 'imexpired', '2018-12-01T00:00:00.0Z', '2018-12-02T00:00:00.0Z', '{"data": 7}', '2018-12-01T00:00:00.0Z'),
  ('888c69c8afe947ba887fd6404428b31c', 100, 'p8', 'notremoved', '2018-12-15T00:00:00.0Z', '2019-12-01T00:00:00.0Z', '{"data": 8}', '2018-12-15T00:00:00.0Z'),
  ('999c69c8afe947ba887fd6404428b31c', 100, 'p9', 'removed', '2018-12-15T00:00:00.0Z', '2019-12-01T00:00:00.0Z', '{"data": 9}', '2018-12-15T00:00:00.0Z');


INSERT INTO feed_channel_status
  (channel_id, feed_id, created, status)
VALUES
  (0, '111c69c8afe947ba887fd6404428b31c', '2018-12-01T00:00:00.0Z', 'published'),
  (0, '222c69c8afe947ba887fd6404428b31c', '2018-12-01T00:00:00.0Z', 'removed'),
  (0, '333c69c8afe947ba887fd6404428b31c', '2018-12-01T00:00:00.0Z', 'published'),
  (0, '444c69c8afe947ba887fd6404428b31c', '2018-12-01T00:00:00.0Z', 'published'),
  (0, '666c69c8afe947ba887fd6404428b31c', '2018-12-01T00:00:00.0Z', 'published'),
  (0, '777c69c8afe947ba887fd6404428b31c', '2018-12-01T00:00:00.0Z', 'published'),
  (0, '888c69c8afe947ba887fd6404428b31c', '2018-12-01T00:00:00.0Z', 'published'),
  (0, '999c69c8afe947ba887fd6404428b31c', '2018-12-01T00:00:00.0Z', 'published'),

  (1, '111c69c8afe947ba887fd6404428b31c', '2018-12-01T00:00:00.0Z', 'removed'),
  (1, '222c69c8afe947ba887fd6404428b31c', '2018-12-01T00:00:00.0Z', 'published'),
  (1, '333c69c8afe947ba887fd6404428b31c', '2018-12-01T00:00:01.0Z', 'read'),
  (1, '555c69c8afe947ba887fd6404428b31c', '2018-12-01T00:00:00.0Z', 'published'),
  (1, '666c69c8afe947ba887fd6404428b31c', '2018-12-01T00:00:00.0Z', 'published');


INSERT INTO remove_requests
  (service_id, request_id, created)
VALUES
  (100, 'notremoved', '2018-12-01T00:00:00.0Z'),
  (100, 'removed', '2018-12-16T00:00:00.0Z');


INSERT INTO feed_payload
(feed_id, channel_id, payload_overrides, payload_params)
VALUES ('444c69c8afe947ba887fd6404428b31c', 0, '{"alert": true}', '{"(number, 4)"}');
