INSERT INTO callcenter_queues.routed_calls
 (id, asterisk_call_id, created_at, call_guid, metaqueue, subcluster)
 VALUES
    ('72387a925925b67ff4042738e19b2fbc492fbf48', NULL, '2020-05-01T10:00:00.00Z', 'call_guid_1', 'disp', 's1'),
    ('4FxYi6+p6gEwLExlHAwMJ/6ZhGU=', NULL, '2020-05-01T10:02:00.00Z', 'call_guid_2', 'disp', 's1');
-- special values, that are created using idempotency token in id
