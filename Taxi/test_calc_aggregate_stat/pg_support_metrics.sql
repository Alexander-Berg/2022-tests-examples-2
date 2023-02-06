INSERT INTO events.chatterbox_events
  (id, type, created_ts, login, action_type, in_addition, line, new_line, start_timestamp)
VALUES
  (
    'action_1', 'chatterbox_action', '2019-07-02 12:00:01.000000+00',
    'superuser', 'create', FALSE, 'first', '', null
  ),
  (
    'action_2', 'chatterbox_action', '2019-07-02 12:00:25.000000+00',
    'superuser', 'create', FALSE, 'second', '', null
  ),
  (
    'action_3', 'chatterbox_action', '2019-07-02 12:00:30.000000+00',
    'superuser', 'create', FALSE, 'first', '', null
  ),
  (
    'action_4', 'chatterbox_action', '2019-07-02 12:00:35.000000+00',
    'superuser', 'create', FALSE, 'third', '', null
  ),
  (
    'action_5', 'chatterbox_action', '2019-07-02 12:01:30.000000+00',
    'support_1', 'create', FALSE, 'second', '', null
  ),
  (
    'action_6', 'chatterbox_action', '2019-07-02 12:00:30.000000+00',
    'support_1', 'forward', FALSE, 'first', 'second', null
  ),
  (
    'action_7', 'chatterbox_action', '2019-07-02 12:00:35.000000+00',
    'support_1', 'forward', FALSE, 'first', 'third', null
  ),
  (
    'action_8', 'chatterbox_action', '2019-07-02 12:00:37.000000+00',
    'support_2', 'forward', FALSE, 'first', 'second', null
  ),
  (
    'action_9', 'chatterbox_action', '2019-07-02 12:00:31.000000+00',
    'support_1', 'forward', FALSE, 'first', 'second', null
  ),
  (
    'action_10', 'chatterbox_action', '2019-07-02 12:01:31.000000+00',
    'support_3', 'forward', FALSE, 'third', 'first', null
  ),
  (
    'action_11', 'chatterbox_action', '2019-07-02 12:03:31.000000+00',
    'support_1', 'forward', FALSE, 'first', 'second', null
  ),
  (
    'action_11.1', 'chatterbox_action', '2019-07-02 12:00:31.000000+00',
    'support_2', 'close', FALSE, 'first', '', null
  ),
  (
    'action_11.2', 'chatterbox_action', '2019-07-02 12:00:31.000000+00',
    'support_2', 'dismiss', FALSE, 'first', '', null
  ),
  (
    'action_11.3', 'chatterbox_action', '2019-07-02 12:00:31.000000+00',
    'support_2', 'export', FALSE, 'first', '', null
  ),
  (
    'action_11.4', 'chatterbox_action', '2019-07-02 12:00:31.000000+00',
    'support_2', 'comment', FALSE, 'first', '', null
  ),
  (
    'action_11.5', 'chatterbox_action', '2019-07-02 12:00:31.000000+00',
    'support_2', 'communicate', FALSE, 'first', '', null
  ),
  (
    'action_12', 'chatterbox_action', '2019-07-02 12:01:32.000000+00',
    'support_1', 'first_accept', FALSE, 'first', 'second', null
  ),
  (
    'action_13', 'chatterbox_action', '2019-07-02 12:01:32.000000+00',
    'support_1', 'ticket_lost', FALSE, 'first', 'second', null
  ),
  (
    'action_14', 'chatterbox_action', '2019-07-02 12:01:32.000000+00',
    'support_1', 'line_sla_success', FALSE, 'first', 'second', null
  ),
  (
    'action_15', 'chatterbox_action', '2019-07-02 12:01:32.000000+00',
    'support_1', 'line_sla_success', FALSE, 'first', 'second', null
  ),
  (
    'action_16', 'chatterbox_action', '2019-07-02 12:01:32.000000+00',
    'support_1', 'line_sla_fail', FALSE, 'first', 'second', null
  ),
  (
    'action_17', 'chatterbox_action', '2019-07-02 12:01:32.000000+00',
    'support_1', 'supporter_sla_success', FALSE, 'first', 'second', null
  ),
  (
    'action_18', 'chatterbox_action', '2019-07-02 12:01:32.000000+00',
    'support_2', 'supporter_sla_fail', FALSE, 'first', 'second', null
  ),
  (
    'action_19', 'chatterbox_action', '2019-07-02 11:01:32.000000+00',
    'support_1', 'first_answer', FALSE, 'first', '', '2019-07-02 10:41:32.000000+00'
  ),
  (
    'action_20', 'chatterbox_action', '2019-07-02 11:59:32.000000+00',
    'support_1', 'first_answer', FALSE, 'first', '', '2019-07-02 11:58:32.000000+00'
  ),
  (
    'action_21', 'chatterbox_action', '2019-07-02 12:01:32.000000+00',
    'support_2', 'first_answer', FALSE, 'second', '', '2019-07-02 12:01:22.000000+00'
  ),
  (
    'action_22', 'chatterbox_action', '2019-07-02 12:04:32.000000+00',
    'support_2', 'first_answer', FALSE, 'second', '', '2019-07-02 12:00:22.000000+00'
  ),
  (
    'action_23', 'chatterbox_action', '2019-07-02 11:59:15.000000+00',
    'support_1', 'first_answer', FALSE, 'first', '', '2019-07-02 11:58:45.000000+00'
  ),
  (
    'action_24', 'chatterbox_action', '2019-07-02 12:01:22.000000+00',
    'support_1', 'first_answer', FALSE, 'second', '', '2019-07-02 12:01:17.000000+00'
  ),
  (
    'action_25', 'chatterbox_action', '2019-07-02 12:01:24.000000+00',
    'support_2', 'first_answer', FALSE, 'second', '', '2019-07-02 12:01:17.000000+00'
  ),
  (
    'action_26', 'chatterbox_action', '2019-07-02 11:01:32.000000+00',
    'support_1', 'online_chat_processing', FALSE, 'first', '', '2019-07-02 11:01:07.000000+00'
  ),
  (
    'action_27', 'chatterbox_action', '2019-07-02 11:59:32.000000+00',
    'support_1', 'online_chat_processing', FALSE, 'first', '', '2019-07-02 11:58:42.000000+00'
  ),
  (
    'action_28', 'chatterbox_action', '2019-07-02 12:01:32.000000+00',
    'support_2', 'online_chat_processing', FALSE, 'second', '', '2019-07-02 12:00:17.000000+00'
  ),
  (
    'action_29', 'chatterbox_action', '2019-07-02 12:04:32.000000+00',
    'support_2', 'online_chat_processing', FALSE, 'second', '', '2019-07-02 12:02:52.000000+00'
  ),
  (
    'action_30', 'chatterbox_action', '2019-07-02 11:59:15.000000+00',
    'support_1', 'online_chat_processing', FALSE, 'first', '', '2019-07-02 11:57:10.000000+00'
  ),
  (
    'action_31', 'chatterbox_action', '2019-07-02 12:01:22.000000+00',
    'support_1', 'online_chat_processing', FALSE, 'second', '', '2019-07-02 11:58:52.000000+00'
  ),
  (
    'action_32', 'chatterbox_action', '2019-07-02 12:01:24.000000+00',
    'support_2', 'online_chat_processing', FALSE, 'second', '', '2019-07-02 11:58:29.000000+00'
  ),
  (
    'action_33', 'chatterbox_action', '2019-07-02 12:01:26.000000+00',
    'support_1', 'online_chat_processing', FALSE, 'first', '', '2019-07-02 11:58:06.000000+00'
  ),
  (
    'action_34', 'chatterbox_action', '2019-07-02 12:01:27.000000+00',
    'support_2', 'online_chat_processing', FALSE, 'first', '', '2019-07-02 11:57:42.000000+00'
  ),
  (
    'action_35', 'sip_call', '2019-07-02 12:01:32.000000+00',
    'support_1', 'success_call', NULL, 'first', '', '2019-07-02 11:56:32.000000+00'
  ),
  (
    'action_36', 'sip_call', '2019-07-02 12:01:32.000000+00',
    'support_1', 'success_call', NULL, 'first', '', '2019-07-02 12:00:32.000000+00'
  ),
  (
    'action_37', 'sip_call', '2019-07-02 12:01:32.000000+00',
    'support_2', 'success_call', NULL, 'first', '', '2019-07-02 11:59:32.000000+00'
  ),
  (
    'action_38', 'sip_call', '2019-07-02 12:01:32.000000+00',
    'support_2', 'failed_call', NULL, 'first', '', '2019-07-02 12:01:32.000000+00'
  ),
  (
    'action_39', 'sip_call', '2019-07-02 12:01:32.000000+00',
    'support_2', 'incoming_call', NULL, 'first', '', '2019-07-02 11:59:32.000000+00'
  ),
  (
    'action_40', 'chatterbox_action', '2019-07-02 11:01:40.000000+00',
    'support_1', 'speed_answer', FALSE, 'first', '', '2019-07-02 11:01:10.000000+00'
  ),
  (
    'action_41', 'chatterbox_action', '2019-07-02 11:59:30.000000+00',
    'support_1', 'speed_answer', FALSE, 'first', '', '2019-07-02 11:58:00.000000+00'
  ),
  (
    'action_42', 'chatterbox_action', '2019-07-02 12:01:45.000000+00',
    'support_1', 'speed_answer', FALSE, 'second', '', '2019-07-02 12:00:30.000000+00'
  ),
  (
    'action_43', 'chatterbox_action', '2019-07-02 12:01:46.000000+00',
    'support_1', 'close', FALSE, 'second', '', null
  );


INSERT INTO events.supporter_events
  (id, type, created_ts, login, status, in_addition, start_timestamp, finish_timestamp, lines, projects)
VALUES
  (
    'support_event_1', 'supporter_status', '2019-07-02 12:00:01.000000+00',
    'supporter_1', 'offline', FALSE, '2019-07-02 10:00:01.000000+00',
    '2019-07-02 11:00:01.000000+00', ARRAY['first'], ARRAY['taxi']
  ),
  (
    'support_event_2', 'supporter_status', '2019-07-02 12:00:01.000000+00',
    'supporter_2', 'offline', FALSE, '2019-07-02 11:59:01.000000+00',
    '2019-07-02 12:04:01.000000+00', ARRAY['first'], ARRAY['taxi']
  ),
  (
    'support_event_3', 'supporter_status', '2019-07-02 12:00:01.000000+00',
    'supporter_1', 'online', FALSE, '2019-07-02 11:00:01.000000+00',
    '2019-07-02 13:00:01.000000+00', ARRAY['first', 'second'], ARRAY['taxi', 'eats']
  ),
  (
    'support_event_4', 'supporter_status', '2019-07-02 11:59:25.000000+00',
    'supporter_1', 'before-break', FALSE, '2019-07-02 11:58:12.000000+00',
    '2019-07-02 12:01:33.000000+00', ARRAY['first', 'second'], ARRAY['taxi', 'eats']
  ),
  (
    'support_event_5', 'supporter_status', '2019-07-02 12:01:42.000000+00',
    'supporter_2', 'online-reversed', FALSE, '2019-07-02 12:00:01.000000+00',
    '2019-07-02 12:01:42.000000+00', ARRAY['second'], ARRAY['taxi']
  ),
  (
    'support_event_6', 'supporter_status', '2019-07-02 12:03:15.000000+00',
    'supporter_3', 'online-reversed', FALSE, '2019-07-02 12:02:30.000000+00',
    '2019-07-02 12:03:55.000000+00', ARRAY['first'], ARRAY['eats']
  ),
  (
    'support_event_7', 'supporter_status', '2019-07-02 12:01:01.000000+00',
    'supporter_2', 'online-reversed', FALSE, '2019-07-02 11:58:10.000000+00',
    '2019-07-02 12:00:15.000000+00', ARRAY['second'], ARRAY['taxi', 'eats']
  ),
  (
    'support_event_8', 'supporter_status', '2019-07-02 12:02:01.000000+00',
    'supporter_1', 'online-reversed', FALSE, '2019-07-02 11:59:55.000000+00',
    '2019-07-02 11:59:58.000000+00', ARRAY['first', 'second'], ARRAY['eats']
  ),
  (
    'support_event_9', 'supporter_status', '2019-07-02 12:01:12.000000+00',
    'supporter_1', 'online-reversed', FALSE, '2019-07-02 11:30:01.000000+00',
    '2019-07-02 12:15:00.000000+00', ARRAY['first'], ARRAY['taxi', 'eats']
  ),
  (
    'support_event_10', 'supporter_status', '2019-07-02 12:00:21.000000+00',
    'supporter_2', 'online-reversed', FALSE, '2019-07-02 12:00:11.000000+00',
    '2019-07-02 12:01:35.000000+00', ARRAY['first', 'second'], ARRAY['taxi']
  ),
  (
    'support_event_11', 'supporter_status', '2019-07-02 12:02:24.000000+00',
    'supporter_3', 'online-reversed', FALSE, '2019-07-02 11:55:00.000000+00',
    '2019-07-02 12:02:25.000000+00', ARRAY['first'], ARRAY['taxi']
  );


INSERT INTO events.chatterbox_lines_backlog_events
  (id, created_ts, line, projects, status, count)
VALUES
  (
    'first_new_2019-07-01T15:55:01', '2019-07-01 15:55:01.000000+00', 'first', ARRAY['taxi'], 'new', 1
  ),
  (
    'first_reopen_2019-07-02T00:55:01', '2019-07-02 00:55:01.000000+00', 'first', ARRAY['taxi'], 'reopen', 2
  ),
  (
    'first_new_2019-07-02T09:55:01', '2019-07-02 09:55:01.000000+00', 'first', ARRAY['taxi'], 'new', 2
  ),
  (
    'first_new_2019-07-02T12:00:01', '2019-07-02 12:00:01.000000+00', 'first', ARRAY['taxi'], 'new', 3
  ),
  (
    'first_reopened_2019-07-02T12:00:01', '2019-07-02 12:00:01.000000+00', 'first', ARRAY['taxi'], 'process', 30
  );


INSERT INTO events.chatterbox_ivr_calls_events
(
    id,
    created_ts,
    line,
    action_type,
    start_timestamp,
    answered_timestamp,
    completed_timestamp
)
VALUES
(
    'call_1', '2019-07-02 12:02:01.000000+00', -- 60
    'telephony', 'success_call', '2019-07-02 12:00:01.000000+00', '2019-07-02 12:01:01.000000+00', '2019-07-02 12:02:01.000000+00'
),
(
    'call_2', '2019-07-02 12:02:01.000000+00', -- 60
    'telephony2', 'success_call', '2019-07-02 12:00:01.000000+00', '2019-07-02 12:01:01.000000+00', '2019-07-02 12:02:01.000000+00'
),
(
    'call_3', '2019-07-02 12:02:01.000000+00', -- 50
    'telephony', 'success_call', '2019-07-02 12:00:01.000000+00', '2019-07-02 12:00:51.000000+00', '2019-07-02 12:01:01.000000+00'
),
(
    'call_4', '2019-07-02 12:02:01.000000+00', -- 4
    'telephony', 'success_call', '2019-07-02 12:00:01.000000+00', '2019-07-02 12:00:05.000000+00', '2019-07-02 12:00:07.000000+00'
),
(
    'call_5', '2019-07-02 12:02:01.000000+00', -- 120
    'telephony', 'missed_call', '2019-07-02 12:00:01.000000+00', NULL, '2019-07-02 12:02:01.000000+00'
),
(
    'call_6', '2019-07-02 12:02:01.000000+00', -- 2
    'telephony', 'missed_call', '2019-07-02 12:00:01.000000+00', NULL, '2019-07-02 12:00:03.000000+00'
),
(
    'call_7', '2019-07-02 12:02:01.000000+00', -- 2
    'telephony2', 'missed_call', '2019-07-02 12:00:01.000000+00', NULL, '2019-07-02 12:00:03.000000+00'
),
(
    'call_8', '2019-07-02 11:02:01.000000+00', -- 60
    'telephony', 'success_call', '2019-07-02 11:00:01.000000+00', '2019-07-02 11:01:01.000000+00', '2019-07-02 11:02:01.000000+00'
),
(
    'call_9', '2019-07-02 12:02:01.000000+00', -- 10
    'telephony', 'success_call', '2019-07-02 12:00:01.000000+00', '2019-07-02 12:00:11.000000+00', '2019-07-02 12:02:01.000000+00'
),
(
    'call_10', '2019-07-02 12:02:01.000000+00', -- 30
    'telephony', 'success_call', '2019-07-02 12:00:01.000000+00', '2019-07-02 12:00:31.000000+00', '2019-07-02 12:02:01.000000+00'
);
