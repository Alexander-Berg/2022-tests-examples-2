INSERT INTO services
  (id, name)
VALUES ('10', 'tariffeditor'),
       ('11', 'other_service');

INSERT INTO feeds
  (feed_id, service_id, request_id, created, expire, payload, publish_at)
VALUES ('3fac69c8afe947ba887fd6404428b31c', '10', 'req_1', '2018-12-01T00:00:00.0Z', '2018-12-01T00:00:00.0Z', '{}', '2018-12-01T00:00:00.0Z'),
       ('4b93b12e57c14d9298f67c94e5f6fe3d', '10', 'req_2', '2018-12-01T00:00:00.0Z', '2018-12-01T00:00:00.0Z', '{}', '2018-12-01T00:00:00.0Z'),
       ('4b93b12e57c14d9298f67c94e5f6fe33', '11', 'req_3', '2018-12-01T00:00:00.0Z', '2018-12-01T00:00:00.0Z', '{}', '2018-12-01T00:00:00.0Z');

INSERT INTO channels
  (id, name, service_id, etag, updated)
VALUES ('0', 'city:moscow', '10', '358af30761eb454db8af9c8f9666e5a8', '2018-12-01T00:00:01.0Z'),
       ('1', 'park:100500', '10', '358af30761eb454db8af9c8f9666e5a8', '2018-12-01T00:00:01.0Z'),
       ('2', 'park:100500', '11', '358af30761eb454db8af9c8f9666e5a8', '2018-12-01T00:00:01.0Z');

INSERT INTO feed_channel_status
  (feed_id, channel_id, created, status)
VALUES ('3fac69c8afe947ba887fd6404428b31c', '0', '2018-12-01T00:00:00.0Z', 'published'),
       ('3fac69c8afe947ba887fd6404428b31c', '1', '2018-12-01T00:00:00.0Z', 'published'),
       ('4b93b12e57c14d9298f67c94e5f6fe3d', '1', '2018-12-01T00:00:00.0Z', 'published'),
       ('4b93b12e57c14d9298f67c94e5f6fe33', '2', '2018-12-01T00:00:00.0Z', 'published');
