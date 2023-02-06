INSERT INTO events.chatterbox_events
  (id, type, created_ts, login, action_type, in_addition, line, new_line, start_timestamp, task_id)
VALUES
  (
    'dismiss_action', 'chatterbox_action', '2022-06-13 06:56:00.000000+00',
    'operator_1', 'dismiss', FALSE, 'eda_first', '', NULL, 'task_1'
  ),
  (
    'reopen_action', 'chatterbox_action', '2022-06-13 06:57:00.000000+00',
    'operator_1', 'reopen', FALSE, 'eda_first', '', NULL, 'task_1'
  );
