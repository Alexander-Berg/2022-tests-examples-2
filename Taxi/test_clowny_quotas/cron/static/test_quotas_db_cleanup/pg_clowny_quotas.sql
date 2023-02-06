INSERT INTO quotas.quotas (ts, resource_provider, data)
VALUES (now(), 'yp_quotas', '{"a": 1, "b": 2}'),
       (now() - INTERVAL '1 days', 'mdb_quotas', '{"a":1, "b": 2}'),
       (now() - INTERVAL '2 days', 'mdb_quotas', '{"a":1, "b": 2}'),
       (now() - INTERVAL '15 days', 'mdb_quotas', '{"a":1, "b": 2}'),
       (now() - INTERVAL '16 days', 'mdb_quotas', '{"a":1, "b": 2}')
;
