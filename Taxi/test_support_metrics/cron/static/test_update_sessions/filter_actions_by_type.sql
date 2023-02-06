INSERT INTO events.chatterbox_events
  (id, type, created_ts, login, action_type, in_addition, line, new_line, start_timestamp, task_id)
VALUES
  (
    'create_action', 'chatterbox_action', '2022-06-13 06:56:00.000000+00',
    'superuser', 'create', FALSE, 'eda_first', '', NULL, 'task_1'
  ),
  (
    'communicate_action', 'chatterbox_action', '2022-06-13 06:57:00.000000+00',
    'operator_1', 'communicate', FALSE, 'eda_first', '', NULL, 'task_1'
  ),
  (
    'close_action', 'chatterbox_action', '2022-06-13 06:58:00.000000+00',
    'operator_1', 'close', FALSE, 'eda_first', '', NULL, 'task_1'
  ),
  (
    'reopen_action', 'chatterbox_action', '2022-06-13 06:56:00.000000+00',
    'superuser', 'reopen', FALSE, 'eda_first', '', NULL, 'task_2'
  ),
  (
    'first_answer_action', 'chatterbox_action', '2022-06-13 06:57:00.000000+00',
    'operator_2', 'first_answer', FALSE, 'eda_first', 'eda_first', NULL, 'task_2'
  ),
  (
    'comment_action', 'chatterbox_action', '2022-06-13 06:58:00.000000+00',
    'operator_2', 'comment', FALSE, 'eda_first', '', NULL, 'task_2'
  ),
  (
    'create_action_2', 'chatterbox_action', '2022-06-13 06:56:00.000000+00',
    'superuser', 'create', FALSE, 'eda_first', '', NULL, 'task_3'
  ),
  (
    'dismiss_action', 'chatterbox_action', '2022-06-13 06:57:00.000000+00',
    'operator_3', 'dismiss', FALSE, 'eda_first', '', NULL, 'task_3'
  );
