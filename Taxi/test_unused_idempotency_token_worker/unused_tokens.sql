INSERT INTO services
  (id, name)
VALUES ('1', 'service'),
       ('2', 'other_service');

INSERT INTO feeds
  (feed_id, service_id, request_id, created, expire, payload, publish_at, token)
VALUES ('11111111111111111111111111111111', '1', 'req_1', '2018-12-01T00:00:00.0Z', '2018-12-11T00:00:00.0Z', '{}', '2018-12-01T00:00:00.0Z', 'token1'),
       ('22222222222222222222222222222222', '2', 'req_1', '2018-12-01T00:00:00.0Z', '2018-12-11T00:00:00.0Z', '{}', '2018-12-01T00:00:00.0Z', 'token2');

INSERT INTO channels
  (id, name, service_id, etag, updated)
VALUES ('0', 'city:moscow', '1', '358af30761eb454db8af9c8f9666e5a8', '2018-12-01T00:00:00.0Z'),
       ('1', 'park:100500', '1', '358af30761eb454db8af9c8f9666e5a8', '2018-12-01T00:00:01.0Z'),
       ('2', 'park:100500', '2', '358af30761eb454db8af9c8f9666e5a8', '2018-12-01T00:00:01.0Z');

INSERT INTO feed_channel_status
  (feed_id, channel_id, created, status)
VALUES ('11111111111111111111111111111111', '0', '2018-12-01T00:00:00.0Z', 'published'),
       ('11111111111111111111111111111111', '1', '2020-12-01T00:00:00.0Z', 'published'),
       ('22222222222222222222222222222222', '2', '2020-12-01T00:00:00.0Z', 'published');

INSERT INTO idempotency_token
   (service_id, idempotency_token, created)
VALUES (1, 'token1', '2018-12-01T00:00:00.0Z'),
       (1, 'token2', '2018-12-01T00:00:00.0Z'),
       (2, 'token2', '2018-12-01T00:00:00.0Z');
