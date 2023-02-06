INSERT INTO
    callcenter_stats.operator_history
    (agent_id, login, status, created_at, queues, prev_status, prev_queues, prev_created_at)
VALUES
    ('agent01', 'l01', 'connected', '2020-06-22T07:30:00Z', array['queue1_on_1'], DEFAULT, DEFAULT, NULL),
    ('agent02', 'l02', 'connected', '2020-06-22T09:50:00Z', array['queue2_on_1'],  DEFAULT, DEFAULT, NULL),
    ('agent02', 'l02', 'paused',    '2020-06-22T09:55:00Z', array['queue2_on_1'],  'connected', array['queue2_on_1'], '2020-06-22T09:50:00Z'),
    ('agent03', 'l03', 'connected', '2020-06-22T09:56:00Z', array['queue1_on_1','queue2_on_1'],  DEFAULT, DEFAULT, NULL)

