INSERT INTO callcenter_queues.calls
    (asterisk_call_id, metaqueue, subcluster, status, queued_at, last_event_at)
VALUES
    ('1','disp','1','queued', NOW() - INTERVAL '24 HOUR', NOW() - INTERVAL '24 HOUR'), -- For deletion
    ('2','disp','1','queued', NOW() - INTERVAL '24 HOUR', NOW() - INTERVAL '24 HOUR'), -- For deletion
    ('3','disp','1','queued', NOW() - INTERVAL '24 HOUR', NOW() - INTERVAL '24 HOUR'), -- For deletion
    ('4','disp','1','queued', NOW() - INTERVAL '24 HOUR', NOW() - INTERVAL '24 HOUR'), -- For deletion
    ('5','disp','1','queued', NOW() - INTERVAL '24 HOUR', NOW() - INTERVAL '24 HOUR'), -- For deletion
    ('6','disp','1','queued', NOW() - INTERVAL '24 HOUR', NOW() - INTERVAL '24 HOUR'), -- For deletion
    ('7','disp','1','queued', NOW() - INTERVAL '24 HOUR', NOW() - INTERVAL '24 HOUR'), -- For deletion
    ('8','disp','1','queued', NOW() - INTERVAL '24 HOUR', NOW() - INTERVAL '24 HOUR'), -- For deletion
    ('9','disp','1','queued', NOW() - INTERVAL '24 HOUR', NOW() - INTERVAL '24 HOUR'), -- For deletion
    ('10','disp','1','queued', NOW() - INTERVAL '24 HOUR', NOW() - INTERVAL '24 HOUR'), -- For deletion
    ('11','disp','1','queued', NOW() - INTERVAL '24 HOUR', NOW() - INTERVAL '24 HOUR'); -- For deletion
