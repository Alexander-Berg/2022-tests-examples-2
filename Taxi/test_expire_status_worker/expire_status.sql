INSERT INTO services
  (id, name)
VALUES
  ('10', 'service'),
  ('20', 'other_service'),
  ('30', 'caching_service');

INSERT INTO feeds
  (feed_id, service_id, request_id, created, expire, payload, publish_at)
VALUES
  ('11111111111111111111111111111111', '10', 'req_1', '2018-12-01T00:00:00.0Z', '2018-12-30T00:00:00.0Z', '{}', '2018-12-01T00:00:00.0Z'),
  ('22222222222222222222222222222222', '20', 'req_2', '2018-12-01T00:00:00.0Z', '2018-12-30T00:00:00.0Z', '{}', '2018-12-01T00:00:00.0Z');

INSERT INTO channels
  (id, name, service_id, etag, updated)
VALUES
  ('0', 'service:user:1', '10', '358af30761eb454db8af9c8f9666e5a8', '2018-12-01T00:00:01.0Z'),
  ('1', 'service:user:2', '10', '358af30761eb454db8af9c8f9666e5a8', '2018-12-01T00:00:01.0Z'),
  ('2', 'other_service:user:1', '20', '358af30761eb454db8af9c8f9666e5a8', '2018-12-01T00:00:01.0Z'),
  ('3', 'other_service:user:2', '20', '358af30761eb454db8af9c8f9666e5a8', '2018-12-01T00:00:01.0Z');

INSERT INTO feed_channel_status
  (feed_id, channel_id, created, expire, status, meta)
VALUES
  ('11111111111111111111111111111111', '0', '2018-12-01T00:00:00.0Z', '2018-12-30T00:00:00.0Z', 'read', '{"a": 1}'::jsonb),
  ('11111111111111111111111111111111', '1', '2018-12-01T00:00:00.0Z', '2018-12-15T00:00:00.0Z', 'read', '{"a": 2}'::jsonb),
  ('22222222222222222222222222222222', '2', '2018-12-01T00:00:00.0Z', '2018-12-15T00:00:00.0Z', 'read', '{"a": 3}'::jsonb),
  ('22222222222222222222222222222222', '3', '2018-12-01T00:00:00.0Z', NULL,                     'read', '{"a": 4}'::jsonb);
