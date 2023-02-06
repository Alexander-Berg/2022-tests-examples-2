INSERT INTO services
  (id, name)
VALUES
  (1, 'service'),
  (2, 'other_service');


INSERT INTO channels
  (id, name, service_id, etag, updated)
VALUES
  (0, 'driver:1', 1, '358af30761eb454db8af9c8f9666e5a8', '2018-12-01T00:00:01.0Z'),
  (1, 'user:1', 2, '358af30761eb454db8af9c8f9666e5a8', '2018-12-01T00:00:01.0Z'),
  (2, 'driver:2', 1, '358af30761eb454db8af9c8f9666e5a8', '2018-12-01T00:00:01.0Z');


INSERT INTO feeds
  (feed_id, service_id, request_id, created, expire, payload, publish_at)
VALUES
  ('111c69c8afe947ba887fd6404428b31c', 1, 'request_1', '2018-12-01T00:00:00.0Z', '2019-12-01T00:00:00.0Z', '{"text": "Best order you can do!", "media_id": "media1"}', '2018-12-02T00:00:00.0Z'),
  ('222c69c8afe947ba887fd6404428b31c', 1, 'request_1', '2018-12-01T00:00:00.0Z', '2019-12-01T00:00:00.0Z', '{"text": "Tariff changes: get extra pie"}', '2018-12-01T00:00:00.0Z'),
  ('333c69c8afe947ba887fd6404428b31c', 2, 'request_2', '2018-12-01T00:00:00.0Z', '2019-12-01T00:00:00.0Z', '{"text": "Test custom media_id field name", "media_id": "media1"}', '2018-12-02T00:00:00.0Z'),
  ('444c69c8afe947ba887fd6404428b31c', 1, 'request_1', '2018-12-01T00:00:00.0Z', '2019-12-01T00:00:00.0Z', '{"text": "Media in S3", "media_id": "media2"}', '2018-12-02T00:00:00.0Z');


INSERT INTO feed_channel_status
  (feed_id, channel_id, created, status, meta)
VALUES
  ('111c69c8afe947ba887fd6404428b31c', 0, '2018-12-01T00:00:00.0Z', 'published', NULL),
  ('222c69c8afe947ba887fd6404428b31c', 0, '2018-12-02T00:00:00.0Z', 'published', NULL),
  ('333c69c8afe947ba887fd6404428b31c', 1, '2018-12-02T00:00:00.0Z', 'published', NULL),
  ('444c69c8afe947ba887fd6404428b31c', 2, '2018-12-02T00:00:00.0Z', 'published', NULL);

INSERT INTO media
  (media_id, media_type, storage_type, storage_settings, updated)
VALUES
  ('media1', 'image', 'avatars', '{"group-id": 1396527, "sizes":
    {
        "orig": {
            "height": 4096,
            "path": "/get-feeds-media/1396527/d8cdff968fc50bf75058753ca0786f38f2b21ae2/orig",
            "width": 4096
        },
        "media-100-100": {
            "height": 100,
            "path": "/get-feeds-media/1396527/d8cdff968fc50bf75058753ca0786f38f2b21ae2/media-100-100",
            "width": 94
        },
        "media-1000-1000": {
            "height": 945,
            "path": "/get-feeds-media/1396527/d8cdff968fc50bf75058753ca0786f38f2b21ae2/media-1000-1000",
            "width": 885
        },
        "media-1000-750": {
            "height": 750,
            "path": "/get-feeds-media/1396527/d8cdff968fc50bf75058753ca0786f38f2b21ae2/media-1000-750",
            "width": 702
        },
        "media-2000-2000": {
            "height": 2000,
            "path": "/get-feeds-media/1396527/d8cdff968fc50bf75058753ca0786f38f2b21ae2/media-2000-2000",
            "width": 2000
        }
      }
    }',
    '2018-12-01T00:00:00.0Z'
  ),
  ('media2', 'image', 's3', '{"bucket_name": "feeds", "service": "taxi"}',
    '2018-12-01T00:00:00.0Z'
  )
;
