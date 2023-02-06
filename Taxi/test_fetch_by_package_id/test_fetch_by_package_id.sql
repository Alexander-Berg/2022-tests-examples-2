INSERT INTO services
(id, name)
VALUES
    (1, 'service'),
    (2, 'other_service');

INSERT INTO channels
(id, name, service_id, etag, updated)
VALUES
    (0, 'channel:1', 1, '358af30761eb454db8af9c8f9666e5a8', '2018-12-01T00:00:01.0Z'),
    (1, 'channel:2', 1, '358af30761eb454db8af9c8f9666e5a8', '2018-12-01T00:00:01.0Z'),
    (2, 'channel:1', 2, '358af30761eb454db8af9c8f9666e5a8', '2018-12-01T00:00:01.0Z'),
    (3, 'channel:2', 2, '358af30761eb454db8af9c8f9666e5a8', '2018-12-01T00:00:01.0Z');

INSERT INTO tags
(service_id, id, name)
VALUES
    (1, 1, 'a'),
    (1, 2, 'b');

INSERT INTO feeds
(feed_id, service_id, package_id, request_id, tags, created, expire, payload, publish_at)
VALUES
    ('111c69c8afe947ba887fd6404428b31c', 1, 'p1', 'request_1', '{1}', '2018-12-01T00:00:00.0Z', '2019-12-01T00:00:00.0Z', '{"text": "feed1"}', '2018-12-01T00:00:00.0Z'),
    ('222c69c8afe947ba887fd6404428b31c', 1, 'p1', 'request_1', '{1, 2}', '2018-12-01T00:00:00.0Z', '2019-12-01T00:00:00.0Z', '{"text": "feed2"}', '2018-12-01T01:00:00.0Z'),
    ('333c69c8afe947ba887fd6404428b31c', 1, 'p1', 'request_1', NULL, '2018-12-01T00:00:00.0Z', '2019-12-01T00:00:00.0Z', '{"text": "feed3"}', '2018-12-01T02:00:00.0Z'),
    ('444c69c8afe947ba887fd6404428b31c', 1, 'p1', 'not_published', NULL, '2018-12-01T00:00:00.0Z', '2019-12-01T00:00:00.0Z', '{"text": "feed4"}', '2019-01-01T00:00:00.0Z'),
    ('555c69c8afe947ba887fd6404428b31c', 1, 'p1', 'expire', NULL, '2018-11-01T00:00:00.0Z', '2018-11-11T00:00:00.0Z', '{"text": "feed5"}', '2018-12-01T00:00:00.0Z'),
    ('666c69c8afe947ba887fd6404428b31c', 1, 'p2', 'not_p1_package_id', NULL, '2018-12-01T00:00:00.0Z', '2019-01-01T00:00:00.0Z', '{"text": "feed6"}', '2018-12-01T00:00:00.0Z');


INSERT INTO feed_channel_status
(feed_id, channel_id, created, status)
VALUES
    ('111c69c8afe947ba887fd6404428b31c', 0, '2018-12-01T00:00:00.0Z', 'published'),
    ('111c69c8afe947ba887fd6404428b31c', 1, '2018-12-02T00:00:00.0Z', 'read'),

    ('222c69c8afe947ba887fd6404428b31c', 0, '2018-12-01T01:00:00.0Z', 'read'),
    ('222c69c8afe947ba887fd6404428b31c', 1, '2018-12-12T01:00:00.0Z', 'published'),

    ('333c69c8afe947ba887fd6404428b31c', 0, '2018-12-01T00:00:00.0Z', 'read'),
    ('333c69c8afe947ba887fd6404428b31c', 1, '2018-12-02T00:00:00.0Z', 'removed'),

    ('444c69c8afe947ba887fd6404428b31c', 2, '2018-12-01T00:00:00.0Z', 'read'),
    ('444c69c8afe947ba887fd6404428b31c', 3, '2018-12-02T00:00:00.0Z', 'removed'),

    ('555c69c8afe947ba887fd6404428b31c', 0, '2018-12-01T00:00:00.0Z', 'published'),

    ('666c69c8afe947ba887fd6404428b31c', 0, '2018-12-01T00:00:00.0Z', 'published');
