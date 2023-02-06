INSERT INTO events.chatterbox_events
  (id, type, created_ts, login, action_type, in_addition, line, new_line, start_timestamp, task_id)
VALUES
  (
    'create_action', 'chatterbox_action', '2022-06-13 06:56:00.000000+00',
    'superuser', 'create', FALSE, 'eda_first', '', NULL, 'task_1'
  ),
  (
    'close_action', 'chatterbox_action', '2022-06-13 06:57:00.000000+00',
    'operator', 'close', FALSE, 'eda_first', '', NULL, 'task_1'
  );

INSERT INTO sessions.chatterbox_sessions
  (task_id, opened_ts, duration, line, login)
VALUES
  ('task_1', '2022-06-13 06:56:00.000000+00', 60, 'eda_first', 'operator');
