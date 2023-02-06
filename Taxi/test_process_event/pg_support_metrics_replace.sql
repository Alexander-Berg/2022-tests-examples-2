INSERT INTO events.supporter_events
  (id, type, created_ts, login, status, in_addition, start_timestamp, finish_timestamp)
VALUES
  (
    'replace_id', 'supporter_status', '2019-07-02 12:00:01.000000+00',
    'superuser', 'online', FALSE, '2019-07-02 12:01:01.000000+00',
    '2019-07-02 12:02:01.000000+00'
  );

INSERT INTO events.chatterbox_events
  (id, type, task_id, created_ts, login, action_type, in_addition, line, new_line)
VALUES
  (
    'replace_id', 'chatterbox_action', 'replace_id', '2019-07-02 12:00:01.000000+00',
    'superuser', 'create', FALSE, 'second', ''
  );
