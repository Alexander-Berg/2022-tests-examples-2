INSERT INTO callcenter_stats.operator_talking_status
    (agent_id, queue, is_talking, updated_at)
VALUES
    ('dt4', 'disp_on_1', true, NOW() - INTERVAL '4 HOUR'),
    ('dt2', 'disp_on_1', true, NOW() - INTERVAL '2 HOUR'),
    ('ht4', 'help_on_1', true, NOW() - INTERVAL '4 HOUR'),
    ('ht2', 'help_on_1', true, NOW() - INTERVAL '2 HOUR');
