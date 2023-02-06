INSERT INTO services
    (id, name)
VALUES (1, 'service');

INSERT INTO feeds
    (feed_id, service_id, request_id, created, expire, payload, publish_at)
VALUES ('75e46d20e0d941c1af604d354dd46ca0', 1, 'my_news', '2018-12-01T00:00:00.0Z', '2022-12-01T00:00:00.0Z',
        '{}', '2018-12-01T00:00:00.0Z'),
       ('38672090b4ef4a3382d064c6d9642971', 1, 'my_news', '2018-12-01T00:00:00.0Z', '2022-12-01T00:00:00.0Z',
        '{}', '2018-12-01T01:00:00.0Z');

INSERT INTO channels
    (id, name, service_id, etag, updated)
VALUES (1, 'user:1', 1, '358af30761eb454db8af9c8f9666e5a8', '2018-12-01T00:00:01.0Z'),
       (2, 'user:2', 1, '358af30761eb454db8af9c8f9666e5a8', '2018-12-01T00:00:01.0Z');

INSERT INTO feed_channel_status
    (feed_id, channel_id, created, status, meta)
VALUES ('75e46d20e0d941c1af604d354dd46ca0', 1, '2018-12-01T00:00:00.0Z', 'published', '{}'),
       ('38672090b4ef4a3382d064c6d9642971', 2, '2018-12-01T00:00:00.0Z', 'published', '{}');


INSERT INTO geo_markers
    (marker_id, feed_id, priority, geo, lon, lat, cluster_ids, meta)
VALUES ('a659567e-a916-4546-a8e8-895ea5d2711e',
        '75e46d20e0d941c1af604d354dd46ca0',
        98,
        ST_SetSRID(ST_Point(-111.91286527715694, 40.791238746327316), 4326)::geography,
        -111.91286527715694,
        40.791238746327316,
        ARRAY[]::UUID[], '3');

INSERT INTO geo_markers
    (marker_id, feed_id, priority, geo, lon, lat, cluster_ids, meta)
VALUES ('d8013ccb-52be-45c5-bdd4-ba67a3704b0c',
        '75e46d20e0d941c1af604d354dd46ca0',
        99,
        ST_SetSRID(ST_Point(-111.90335549087736, 40.76243608032395), 4326)::geography,
        -111.90335549087736,
        40.76243608032395,
        ARRAY[]::UUID[], '2');

INSERT INTO geo_markers
    (marker_id, feed_id, priority, geo, lon, lat, cluster_ids, meta)
VALUES ('95671cb4-5e3b-4e8d-a422-25a3c51853bd',
        '38672090b4ef4a3382d064c6d9642971',
        100,
        ST_SetSRID(ST_Point(-111.85847680507557, 40.7017362280835), 4326)::geography,
        -111.85847680507557,
        40.7017362280835,
        ARRAY[]::UUID[], '1');
