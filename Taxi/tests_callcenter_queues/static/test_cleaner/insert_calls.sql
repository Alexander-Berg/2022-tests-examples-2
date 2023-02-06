INSERT INTO callcenter_queues.calls
    (asterisk_call_id, metaqueue, subcluster, status, queued_at, last_event_at)
VALUES
    ('dm4','disp','1','queued', NOW() - INTERVAL '4 HOUR', NOW() - INTERVAL '4 HOUR'),
    ('dm2','disp','1','queued', NOW() - INTERVAL '2 HOUR', NOW() - INTERVAL '2 HOUR'),
    ('dq4','disp','1','queued', NOW() - INTERVAL '4 HOUR', NOW() - INTERVAL '4 HOUR'),
    ('dq2','disp','1','queued', NOW() - INTERVAL '2 HOUR', NOW() - INTERVAL '2 HOUR'),
    ('dt4','disp','1','talking', NOW() - INTERVAL '25 HOUR', NOW() - INTERVAL '4 HOUR'),
    ('dt2','disp','1','talking', NOW() - INTERVAL '25 HOUR', NOW() - INTERVAL '2 HOUR'),
    ('hm4','help','1','queued', NOW() - INTERVAL '4 HOUR', NOW() - INTERVAL '4 HOUR'),
    ('hm2','help','1','queued', NOW() - INTERVAL '2 HOUR', NOW() - INTERVAL '2 HOUR'),
    ('hq4','help','1','queued', NOW() - INTERVAL '4 HOUR', NOW() - INTERVAL '4 HOUR'),
    ('hq2','help','1','queued', NOW() - INTERVAL '2 HOUR', NOW() - INTERVAL '2 HOUR'),
    ('ht4','help','1','talking', NOW() - INTERVAL '25 HOUR', NOW() - INTERVAL '4 HOUR'),
    ('ht2','help','1','talking', NOW() - INTERVAL '25 HOUR', NOW() - INTERVAL '2 HOUR');
