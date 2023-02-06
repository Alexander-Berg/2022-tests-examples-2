INSERT INTO events.chatterbox_events
  (id, type, created_ts, login, action_type, in_addition, line, new_line, start_timestamp, task_id)
VALUES
  (
    'action_outside_time_window', 'chatterbox_action', '2022-06-13 06:54:59.000000+00',
    'superuser', 'create', FALSE, 'eda_first', '', NULL, 'task_1'
  ),
  (
    'action_inside_time_window', 'chatterbox_action', '2022-06-13 06:55:01.000000+00',
    'superuser', 'create', FALSE, 'eda_first', '', NULL, 'task_1'
  );
