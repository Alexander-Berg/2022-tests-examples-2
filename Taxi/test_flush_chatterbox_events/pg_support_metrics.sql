INSERT INTO events.chatterbox_events
  (id, type, created_ts, login, action_type, in_addition, line, new_line, start_timestamp)
VALUES
  (
    'action_1', 'chatterbox_action', '2019-07-01 12:00:01.000000+00',
    'superuser', 'create', FALSE, 'first', '', null
  ),
  (
    'action_2', 'chatterbox_action', '2019-07-02 12:00:25.000000+00',
    'superuser', 'create', FALSE, 'second', '', null
  ),
  (
    'action_3', 'chatterbox_action', '2019-07-03 12:00:30.000000+00',
    'superuser', 'create', FALSE, 'first', '', null
  ),
  (
    'action_4', 'chatterbox_action', '2019-07-04 12:00:35.000000+00',
    'superuser', 'create', FALSE, 'third', '', null
  ),
  (
    'action_5', 'chatterbox_action', '2019-07-05 12:01:30.000000+00',
    'support_1', 'create', FALSE, 'second', '', null
  ),
  (
    'action_6', 'chatterbox_action', '2019-07-06 12:00:30.000000+00',
    'support_1', 'forward', FALSE, 'first', 'second', null
  ),
  (
    'action_7', 'chatterbox_action', '2019-07-07 12:00:35.000000+00',
    'support_1', 'forward', FALSE, 'first', 'third', null
  ),
  (
    'action_8', 'chatterbox_action', '2019-07-08 12:00:37.000000+00',
    'support_2', 'forward', FALSE, 'first', 'second', null
  ),
  (
    'action_9', 'chatterbox_action', '2019-07-09 12:00:31.000000+00',
    'support_1', 'forward', FALSE, 'first', 'second', null
  ),
  (
    'action_10', 'chatterbox_action', '2019-07-10 12:01:31.000000+00',
    'support_3', 'forward', FALSE, 'third', 'first', null
  ),
  (
    'action_11', 'chatterbox_action', '2019-07-11 12:03:31.000000+00',
    'support_1', 'forward', FALSE, 'first', 'second', null
  ),
  (
    'action_12', 'chatterbox_action', '2019-07-12 12:01:32.000000+00',
    'support_1', 'first_accept', FALSE, 'first', 'second', null
  ),
  (
    'action_13', 'chatterbox_action', '2019-07-13 12:01:32.000000+00',
    'support_1', 'ticket_lost', FALSE, 'first', 'second', null
  ),
  (
    'action_14', 'chatterbox_action', '2019-07-14 12:01:32.000000+00',
    'support_1', 'line_sla_success', FALSE, 'first', 'second', null
  )
;
