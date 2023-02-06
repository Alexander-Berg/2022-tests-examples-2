INSERT INTO qc_pools.passes
(id, entity_id, entity_type, exam, created)
VALUES
    ('id1', 'entity_id1', 'driver', 'extra', NOW());
  

INSERT INTO qc_pools.pools
(pool, pass_id, status, created_at, expire_at)
VALUES ('pool3', 'id1', 'processed', '2020-01-01T00:00:00+00:00', '2020-01-01T01:00:00+00:00');

INSERT INTO qc_pools.meta
(pass_id, key, value, data_type, json_value)
VALUES ('id1', 'pool1.sanctions', '["sanction1"]', 'set_string', '["sanction1"]'  )
