INSERT INTO events.chatterbox_events
  (id, type, created_ts, login, action_type, in_addition, line, new_line, start_timestamp, task_id)
VALUES
  (
    'close_action', 'chatterbox_action', '2022-06-13 06:56:00.000000+00',
    'operator_1', 'close', FALSE, 'eda_first', '', NULL, 'task_1'
  ),
  (
    'reopen_action', 'chatterbox_action', '2022-06-13 06:56:00.000000+00',
    'superuser', 'reopen', FALSE, 'eda_first', '', NULL, 'task_2'
  ),
  (
    'close_action_2', 'chatterbox_action', '2022-06-13 06:57:00.000000+00',
    'operator_2', 'close', FALSE, 'eda_first', '', NULL, 'task_2'
  ),
  (
    'reopen_action_2', 'chatterbox_action', '2022-06-13 06:56:00.000000+00',
    'superuser', 'reopen', FALSE, 'eda_first', '', NULL, 'task_3'
  ),
  (
    'create_action', 'chatterbox_action', '2022-06-13 06:55:30.000000+00',
    'superuser', 'reopen', FALSE, 'eda_first', '', NULL, 'task_4'
  ),
  (
    'comment_action', 'chatterbox_action', '2022-06-13 06:56:00.000000+00',
    'operator_3', 'comment', FALSE, 'eda_first', '', NULL, 'task_4'
  ),
  (
    'reopen_action_3', 'chatterbox_action', '2022-06-13 06:57:00.000000+00',
    'superuser', 'reopen', FALSE, 'eda_first', '', NULL, 'task_4'
  ),
  (
    'dismiss_action', 'chatterbox_action', '2022-06-13 06:58:00.000000+00',
    'operator_3', 'dismiss', FALSE, 'eda_first', '', NULL, 'task_4'
  );

INSERT INTO sessions.chatterbox_sessions
  (task_id, opened_ts, duration, line, login)
VALUES
  ('task_1', '2022-06-13 06:54:00.000000+00', NULL, NULL, NULL),
  ('task_2', '2022-06-13 06:54:00.000000+00', NULL, NULL, NULL),
  ('task_3', '2022-06-13 06:54:00.000000+00', NULL, NULL, NULL),
  ('task_4', '2022-06-13 06:55:30.000000+00', 30, 'eda_first', 'operator_3'),
  ('task_4', '2022-06-13 06:57:00.000000+00', NULL, NULL, NULL);
