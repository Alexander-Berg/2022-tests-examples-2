INSERT INTO events.chatterbox_events
  (id, type, created_ts, login, action_type, in_addition, line, new_line, start_timestamp, task_id)
VALUES
  (
    'action_on_eda_first', 'chatterbox_action', '2022-06-13 06:56:00.000000+00',
    'superuser', 'create', FALSE, 'eda_first', '', NULL, 'task_1'
  ),
  (
    'action_on_eda_second', 'chatterbox_action', '2022-06-13 06:56:00.000000+00',
    'superuser', 'create', FALSE, 'eda_second', '', NULL, 'task_1'
  );
