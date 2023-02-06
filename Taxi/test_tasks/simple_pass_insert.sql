INSERT INTO qc_pools.passes
    (id, entity_id, entity_type, exam, created)
VALUES ('id1', '7ad36bc7560449998acbe2c57a75c293_1b3b56986cfc4b4cab35cdab928e2ea6', 'driver', 'dkvu', NOW());

INSERT INTO qc_pools.pools
(pool, pass_id, status, created_at, expire_at)
VALUES ('pool1', 'id1', 'new', '2020-01-01T00:00:00+00:00', '2020-01-01T01:00:00+00:00');
