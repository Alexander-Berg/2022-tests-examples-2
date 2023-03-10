INSERT INTO services
  (id, name)
VALUES ('10', 'tariffeditor');

INSERT INTO feeds
  (feed_id, service_id, request_id, created, expire, payload, publish_at)
VALUES ('11111111111111111111111111111111', '10', 'req_1', '2018-12-01T00:00:00.0Z', '2018-12-11T00:00:00.0Z', '{}', '2018-12-01T00:00:00.0Z'),
       ('22222222222222222222222222222222', '10', 'req_2', '2018-12-01T00:00:00.0Z', '2018-12-11T00:00:00.0Z', '{}', '2018-12-01T00:00:00.0Z'),
       ('33333333333333333333333333333333', '10', 'req_3', '2018-12-01T00:00:00.0Z', '2018-12-11T00:00:00.0Z', '{}', '2018-12-01T00:00:00.0Z'),
       ('44444444444444444444444444444444', '10', 'req_4', '2020-01-01T00:00:00.0Z', '2020-01-22T00:00:00.0Z', '{}', '2020-01-01T00:00:00.0Z'),
       ('55555555555555555555555555555555', '10', 'req_5', '2020-01-02T00:00:00.0Z', null, '{}', '2020-01-02T00:00:00.0Z');

INSERT INTO channels
  (id, name, service_id, etag, updated)
VALUES ('0', 'city:moscow', '10', '358af30761eb454db8af9c8f9666e5a8', '2018-12-01T00:00:01.0Z'),
       ('1', 'park:100500', '10', '358af30761eb454db8af9c8f9666e5a8', '2018-12-01T00:00:01.0Z'),
       ('2', 'park:100501', '10', '558af30761eb454db8af9c8f9666e5a5', '2020-01-01T00:00:00.0Z');

INSERT INTO feed_channel_status
  (feed_id, channel_id, created, status)
VALUES ('11111111111111111111111111111111', '0', '2018-12-01T00:00:00.0Z', 'published'),
       ('11111111111111111111111111111111', '1', '2018-12-01T00:00:00.0Z', 'published'),
       ('22222222222222222222222222222222', '1', '2018-12-01T00:00:00.0Z', 'published'),
       ('33333333333333333333333333333333', '2', '2020-01-01T00:00:00.0Z', 'published'),
       ('44444444444444444444444444444444', '2', '2020-01-01T00:00:00.0Z', 'published'),
       ('55555555555555555555555555555555', '2', '2020-01-01T00:00:00.0Z', 'published');

INSERT INTO feed_payload
(feed_id, channel_id, payload_overrides, payload_params)
VALUES ('33333333333333333333333333333333', 1, '{"alert": true}', NULL);
