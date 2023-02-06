INSERT INTO sessions.chatterbox_sessions
  (task_id, opened_ts, duration, line, login)
VALUES
  ('task_1', '2019-07-02 11:59:25.000000+00', NULL, NULL, NULL),
  ('task_2', '2019-07-02 11:59:30.000000+00', 10, 'line_1', 'operator_1'),
  ('task_2', '2019-07-02 11:59:45.000000+00', 15, 'line_1', 'operator_2'),
  ('task_3', '2019-07-02 12:00:00.000000+00', 60, 'line_2', 'operator_1'),
  ('task_3', '2019-07-02 12:01:00.000000+00', 45, 'line_2', 'operator_2');
