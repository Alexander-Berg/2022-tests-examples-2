INSERT INTO events.chatterbox_events
  (id, type, created_ts, login, action_type, in_addition, line, start_timestamp)
VALUES
  (
    'task_1_1_first_answer_in_line', 'chatterbox_action', '2021-07-18 23:08:01.000000+00',
    'superuser', 'first_answer_in_line', FALSE, 'first', '2021-07-18 23:07:01.000000+00'
  ),
  (
    'task_1_2_first_answer_in_line', 'chatterbox_action', '2021-07-19 23:10:01.000000+00',
    'superuser', 'first_answer_in_line', FALSE, 'second', '2021-07-19 23:06:01.000000+00'
  ),
  (
    'task_2_1_first_answer_in_line', 'chatterbox_action', '2021-07-19 23:12:11.000000+00',
    'superuser', 'first_answer_in_line', FALSE, 'second', '2021-07-19 23:12:01.000000+00'
  ),
  (
    'task_3_1_first_answer_in_line', 'chatterbox_action', '2021-07-19 23:12:11.000000+00',
    'superuser', 'first_answer_in_line', FALSE, 'third', '2021-07-19 22:12:01.000000+00'
  );

INSERT INTO events.chatterbox_ivr_calls_events
(id, created_ts, line, action_type, start_timestamp, answered_timestamp, completed_timestamp)
VALUES
(
    'task_1_calls_count', '2021-07-18 23:08:01.000000+00',
    'first', 'success_call', '2021-07-18 23:07:01.000000+00',
    '2021-07-18 23:07:41.000000+00', '2021-07-18 23:08:41.000000+00'
),
(
    'task_2_calls_count', '2021-07-19 23:10:01.000000+00',
    'first', 'success_call', '2021-07-19 23:06:01.000000+00',
    '2021-07-19 23:06:31.000000+00', '2021-07-19 23:07:01.000000+00'
),
(
    'task_3_calls_count', '2021-07-19 23:12:04.000000+00',
    'second', 'success_call', '2021-07-19 23:12:01.000000+00',
    '2021-07-19 23:12:25.000000+00', '2021-07-19 23:14:01.000000+00'
),
(
    'task_4_calls_count', '2021-07-19 23:12:04.000000+00',
    'first', 'missed_call', '2021-07-19 22:12:01.000000+00',
    NULL, '2021-07-19 22:12:51.000000+00'
),
(
    'task_5_calls_count', '2021-07-19 23:12:07.000000+00',
    'first', 'success_call', '2021-07-19 23:06:01.000000+00',
    '2021-07-19 23:07:01.000000+00', '2021-07-19 23:08:01.000000+00'
),
(
    'task_6_calls_count', '2021-07-19 23:12:07.000000+00',
    'second', 'missed_call', '2021-07-19 23:06:01.000000+00',
    NULL, '2021-07-19 23:08:01.000000+00'
),
(
    'task_7_calls_count', '2022-07-19 23:12:07.000000+00',
    'second', 'missed_call', '2022-07-19 23:06:01.000000+00',
    NULL, '2022-07-19 23:08:01.000000+00'
);
