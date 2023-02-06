INSERT INTO services
  (id, name)
VALUES
  (1, 'service'),
  (2, 'other_service');

INSERT INTO feeds
  (feed_id, service_id, request_id, created, expire, payload, publish_at)
VALUES ('3fac69c8afe947ba887fd6404428b31c', 1, 'req_1', '2018-12-01T00:00:00.0Z', '2018-12-02T00:00:00.0Z', '{}', '2018-12-01T00:00:00.0Z'),
       ('4b93b12e57c14d9298f67c94e5f6fe3d', 1, 'req_2', '2018-12-01T00:00:00.0Z', '2018-12-02T00:00:00.0Z', '{}', '2018-12-01T00:00:00.0Z'),
       ('4b93b12e57c14d9298f67c94e5f6fe33', 2, 'req_3', '2018-12-01T00:00:00.0Z', '2018-12-02T00:00:00.0Z', '{}', '2018-12-01T00:00:00.0Z');

INSERT INTO channels
  (id, name, service_id, etag, updated)
VALUES (14, 'city:moscow', 1, '358af30761eb454db8af9c8f9666e5a8', '2018-12-01T00:00:01.0Z'),
       (15, 'park:1', 1, '358af30761eb454db8af9c8f9666e5a8', '2018-12-01T00:00:01.0Z'),
       (16, 'park:2', 1, '358af30761eb454db8af9c8f9666e5a8', '2018-12-01T00:00:01.0Z');

INSERT INTO feed_channel_status
  (feed_id, channel_id, created, status)
VALUES ('3fac69c8afe947ba887fd6404428b31c', 14, '2018-12-01T00:00:00.0Z', 'published'),
       ('3fac69c8afe947ba887fd6404428b31c', 15, '2018-12-01T00:00:00.0Z', 'published'),
       ('3fac69c8afe947ba887fd6404428b31c', 16, '2018-12-01T00:00:00.0Z', 'read'),
       ('4b93b12e57c14d9298f67c94e5f6fe3d', 15, '2018-12-01T00:00:00.0Z', 'published');
