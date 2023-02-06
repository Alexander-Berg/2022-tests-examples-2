INSERT INTO callcenter_stats.call_status
    (call_id, queue, status, queued_at, answered_at)
VALUES
    ('dm4','disp_on_1','meta', NOW() - INTERVAL '4 HOUR', null),
    ('dm2','disp_on_1','meta', NOW() - INTERVAL '2 HOUR', null),
    ('dq4','disp_on_1','queued', NOW() - INTERVAL '4 HOUR', null),
    ('dq2','disp_on_1','queued', NOW() - INTERVAL '2 HOUR', null),
    ('dt4','disp_on_1','talking', NOW() - INTERVAL '25 HOUR', NOW() - INTERVAL '4 HOUR'),
    ('dt2','disp_on_1','talking', NOW() - INTERVAL '25 HOUR', NOW() - INTERVAL '2 HOUR'),
    ('hm4','help_on_1','meta', NOW() - INTERVAL '4 HOUR', null),
    ('hm2','help_on_1','meta', NOW() - INTERVAL '2 HOUR', null),
    ('hq4','help_on_1','queued', NOW() - INTERVAL '4 HOUR', null),
    ('hq2','help_on_1','queued', NOW() - INTERVAL '2 HOUR', null),
    ('ht4','help_on_1','talking', NOW() - INTERVAL '25 HOUR', NOW() - INTERVAL '4 HOUR'),
    ('ht2','help_on_1','talking', NOW() - INTERVAL '25 HOUR', NOW() - INTERVAL '2 HOUR');
