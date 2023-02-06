INSERT INTO services
  (id, name)
VALUES ('1', 'service'),
       ('2', 'other_service');

INSERT INTO feeds
  (feed_id, service_id, request_id, created, expire, payload, publish_at)
VALUES ('11111111111111111111111111111111', '1', 'req_1', '2018-12-01T00:00:00.0Z', '2018-12-11T00:00:00.0Z', '{}', '2018-12-01T00:00:00.0Z');

INSERT INTO channels
  (id, name, service_id, etag, updated)
VALUES ('0', 'city:moscow', '1', '358af30761eb454db8af9c8f9666e5a8', '2018-12-01T00:00:00.0Z'),
       ('1', 'park:100500', '1', '358af30761eb454db8af9c8f9666e5a8', '2018-12-01T00:00:01.0Z'),
       ('2', 'park:100501', '1', '558af30761eb454db8af9c8f9666e5a5', '2020-01-01T00:00:00.0Z'),
       ('3', 'park:100502', '1', '558af30761eb454db8af9c8f9666e5a5', '2019-01-01T00:00:00.0Z'),
       ('4', 'park:100503', '1', '558af30761eb454db8af9c8f9666e5a5', '2019-01-01T00:00:00.0Z');

INSERT INTO feed_channel_status
  (feed_id, channel_id, created, status)
VALUES ('11111111111111111111111111111111', '0', '2018-12-01T00:00:00.0Z', 'published'),
       ('11111111111111111111111111111111', '1', '2020-12-01T00:00:00.0Z', 'published');
