INSERT INTO callcenter_queues.calls
(asterisk_call_id, metaqueue, subcluster, status, queued_at, last_event_at, routing_id, abonent_phone_id, called_number)
VALUES
    ('dm1','disp','1','queued', NOW() - INTERVAL '4 HOUR', NOW() - INTERVAL '4 HOUR', 'test_1', 'test_phone_id', '+71234567890'),
    ('dm2','disp','1','queued', NOW() - INTERVAL '4 HOUR', NOW() - INTERVAL '4 HOUR', 'test_2', null, '+71234567890'),
    ('dm3','disp','1','queued', NOW() - INTERVAL '4 HOUR', NOW() - INTERVAL '4 HOUR', 'test_3', 'test_phone_id', null);
