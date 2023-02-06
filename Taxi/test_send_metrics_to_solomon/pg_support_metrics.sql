INSERT INTO events.chatterbox_events
  (id, type, task_id, created_ts, login, action_type, in_addition, line, new_line)
VALUES
  (
    'test_duplicate_protection', 'chatterbox_action', 'replace_id', '2019-05-04 12:19:00.000000+00',
    'superuser', 'create', FALSE, 'eda_online', ''
  );
