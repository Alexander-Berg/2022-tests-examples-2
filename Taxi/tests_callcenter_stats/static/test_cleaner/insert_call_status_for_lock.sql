INSERT INTO callcenter_stats.call_status
    (call_id, queue, status, queued_at)
VALUES
    ('1','disp_on_1','queued', NOW() - INTERVAL '24 HOUR'), -- For deletion
    ('2','disp_on_1','queued', NOW() - INTERVAL '24 HOUR'), -- For deletion
    ('3','disp_on_1','queued', NOW()); -- Not for deletion
