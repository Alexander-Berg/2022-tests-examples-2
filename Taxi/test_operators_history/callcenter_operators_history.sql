INSERT INTO callcenter_stats.operator_history
(id, agent_id, created_at, status, queues, login, sub_status)
VALUES
(1, '111', '2020-07-07 12:30:00+0000', 'paused', array['q1', 'q2'], 'test_login1', NULL),
(2, '222', '2020-07-07 12:30:00+0000', 'paused', array['q1', 'q2', 'q3'], 'test_login2', 'break'),
(3, '1000000016', '2020-07-07 12:30:00+0000', 'connected', ARRAY[]::VARCHAR[], 'test_login3', NULL),
(5, '1000000018', '2020-07-07 12:30:00+0000', 'paused', array['q1'], 'test_login4', NULL),
(7, '1000000017', '2020-07-07 12:30:00+0000', 'connected', array['q2'], 'test_login5', NULL),
(8, 'dont_exist', '2020-07-07 12:30:00+0000', 'paused', array['q2'], 'test_login6', NULL),
(9, '1000000013', '2020-07-07 12:30:00+0000', 'paused', array['ru_taxi_disp_on_2'], 'test_login7', NULL);
