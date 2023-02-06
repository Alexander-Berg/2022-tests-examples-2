INSERT INTO services
  (id, name)
VALUES
  (1, 'service'),
  (100, 'caching_service');


INSERT INTO channels
  (id, name, service_id, etag, updated)
VALUES
  (1, 'channel', 1, '358af30761eb454db8af9c8f9666e5a8', '2018-12-01T00:00:01.0Z'),
  (2, 'geo_channel', 1, '358af30761eb454db8af9c8f9666e5a8', '2018-12-01T00:00:01.0Z'),
  (100, 'channel', 100, '358af30761eb454db8af9c8f9666e5a8', '2018-12-01T00:00:01.0Z');


INSERT INTO tags
  (id, name, service_id)
VALUES
  (1, 'a', 1),
  (2, 'b', 1),
  (3, 'a', 100);


INSERT INTO feeds
  (feed_id, service_id, publish_at, tags, request_id, created, expire, payload)
VALUES
  ('111c69c8afe947ba887fd6404428b31c', 1, '2018-12-01T00:00:00.0Z', NULL, 'r', '2018-12-01T00:00:00.0Z', NULL, '{}'),
  ('222c69c8afe947ba887fd6404428b31c', 1, '2018-12-02T00:00:00.0Z', '{1}', 'r', '2018-12-01T00:00:00.0Z', NULL, '{}'),
  ('333c69c8afe947ba887fd6404428b31c', 1, '2018-12-03T00:00:00.0Z', '{1,2}', 'r', '2018-12-01T00:00:00.0Z', NULL, '{}'),
  ('444c69c8afe947ba887fd6404428b31c', 1, '2018-12-03T00:00:00.0Z', '{1}', 'r', '2018-12-01T00:00:00.0Z', NULL, '{}'),
  ('999c69c8afe947ba887fd6404428b31c', 100, '2018-12-01T00:00:00.0Z', NULL, 'r', '2018-12-01T00:00:00.0Z', NULL, '{}');

INSERT INTO geo_markers
    (marker_id, feed_id, priority, geo, lon, lat, cluster_ids)
VALUES ('d8013ccb-52be-45c5-bdd4-ba67a3704b0c', '444c69c8afe947ba887fd6404428b31c', 1,
        ST_Buffer(ST_SetSRID(ST_Point(38.119090, 55.597042), 4326)::geography, 3300)::geography, 38.119090, 55.597042,
        ARRAY[]::UUID[]);


INSERT INTO feed_channel_status
  (feed_id, channel_id, created, status)
VALUES
  ('111c69c8afe947ba887fd6404428b31c', 1, '2018-12-02T00:00:00.0Z', 'published'),
  ('222c69c8afe947ba887fd6404428b31c', 1, '2018-12-01T00:00:00.0Z', 'published'),
  ('333c69c8afe947ba887fd6404428b31c', 1, '2018-12-01T00:00:00.0Z', 'published'),
  ('444c69c8afe947ba887fd6404428b31c', 2, '2018-12-01T00:00:00.0Z', 'published'),
  ('999c69c8afe947ba887fd6404428b31c', 100, '2018-12-01T00:00:00.0Z', 'published');
