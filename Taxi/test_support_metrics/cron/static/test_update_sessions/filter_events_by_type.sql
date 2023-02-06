INSERT INTO events.chatterbox_events
  (id, type, created_ts, login, action_type, in_addition, line, new_line, start_timestamp, task_id)
VALUES
  (
    'action', 'chatterbox_action', '2022-06-13 06:56:00.000000+00',
    'superuser', 'create', FALSE, 'eda_first', '', NULL, 'task_1'
  ),
  (
    'call', 'sip_call', '2022-06-13 06:56:00.000000+00',
    'superuser', 'create', FALSE, 'eda_first', '', NULL, NULL
  );
