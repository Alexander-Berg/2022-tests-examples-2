INSERT INTO qc_pools.passes
(id, entity_id, entity_type, exam, created)
VALUES
    ('id1', '7ad36bc7560449998acbe2c57a75c293_1b3b56986cfc4b4cab35cdab928e2ea6', 'driver', 'dkvu', NOW()),
    ('id2', '7ad36bc7560449998gcbe2c57a75c293_1b3b56986dfc4b4cab35cdab928e2ea6', 'driver', 'dkvu', NOW()),
    ('id3', '7ad36bl7560449998acbe2c57a75c293_1b3b56986ufc4b4cab35cdab928e2ea6', 'driver', 'dkvu', NOW()),
    ('id4', '7ad36bl7560449998acbe2s57a75c293_1b3b56986ufc4b4cab55cdab928e2ea6', 'driver', 'dkvu', NOW());

INSERT INTO qc_pools.pools
(pool, pass_id, status, created_at, expire_at)
VALUES ('pool1', 'id1', 'pending', '2020-01-01T00:00:00+00:00', '2020-01-01T01:00:00+00:00'),
       ('pool2', 'id2', 'processed', '2020-01-01T00:00:00+00:00', '2020-01-01T01:00:00+00:00'),
       ('pool2', 'id4', 'new', '2020-01-01T00:00:00+00:00', '2020-01-01T01:00:00+00:00'),
       ('pool1', 'id3', 'pending', '2020-01-01T00:00:00+00:00', '2120-01-01T03:00:00+00:00'); -- костыль на века
