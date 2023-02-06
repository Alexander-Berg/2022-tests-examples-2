INSERT INTO callcenter_stats.operator_status
    (agent_id, updated_at, status, status_updated_at, queues, login, sub_status, sub_status_updated_at)
VALUES
    ('123456', '2020-07-07 13:00:00+0000', 'paused', '2020-07-07 12:00:00+0000', array['q1', 'q2'], 'test_login', 'break', '2020-07-07 13:00:00+0000');
