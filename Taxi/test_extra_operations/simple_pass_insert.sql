INSERT INTO qc_pools.passes
(id, entity_id, entity_type, exam, created)
VALUES
    ('id1', 'entity_id1', 'driver', 'extra', NOW());
  

INSERT INTO qc_pools.pools
(pool, pass_id, status, created_at, expire_at)
VALUES ('pool2', 'id1', 'processed', '2020-01-01T00:00:00+00:00', '2020-01-01T01:00:00+00:00');
