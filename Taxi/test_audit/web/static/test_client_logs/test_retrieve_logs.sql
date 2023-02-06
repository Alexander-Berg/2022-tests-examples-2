insert into audit_events.systems (
    name
)
values (
    'system_audit'
),
(
    'meta_system'
),
(
    'tplatform'
),
(
    'tariff-editor'
);

insert into audit_events.actions (
    action,
    system_id
)
values (
    'create_value',
    1
),
(
    'update_value',
    1
),
(
    'delete_value',
    1
),
(
    'set_tariff',
    3
);

insert into audit_events.logs (
    id,
    action_id,
    login,
    object_id,
    ticket,
    timestamp,
    request_id,
    arguments,
    system_id,
    tplatform_namespace
)
values (
    'object_id',
    1,
    'deoevgen',
    'create_test_logins',
    'ticket-1',
    '2020-11-27:00:00:00',
    'set_log_1',
     '{
      "_id": "1",
      "body": {
        "a": "wat?"
      }
    }',
    1,
    null
),
(
    'object_id_2',
    2,
    'deoevgen',
    'update_test_logins',
    'ticket-2',
    '2020-11-28:00:00:00',
    'set_log_2',
    '{
      "_id": "2",
      "body": {
        "a": "wat??"
      }
    }',
    1,
    null
),
(
    'object_id_3',
    3,
    'deoevgen',
    'delete_test_logins',
    'ticket-3',
    '2020-11-29:00:00:00',
    'set_log_3',
     '{
      "_id": "3",
      "body": {
        "a": "wat??"
      }
    }',
    1,
    null
),
(
    'object_id_4',
    1,
    'karachevda',
    'create_test_logins',
    null,
    '2020-11-30:00:00:00',
    'set_log_4',
    '{}',
    1,
    null
),
(
    'object_id_5',
    1,
    'deoevgen',
    'create_test_logins',
    null,
    '2020-11-30:10:00:00',
    'set_log_5',
    '{}',
    2,
    null
),
(
    'object_id_6',
    4,
    'vstimchenko',
    'some_object',
    'ticket-2',
    '2020-11-30:12:00:00',
    'set_log_6',
    '{
      "_id": "4",
      "body": {
        "a": "wat??"
      }
    }',
    3,
    null
),
(
    'object_id_7',
    4,
    'antonvasyuk',
    'some_object',
    'ticket-3',
    '2022-01-14:14:00:00',
    'set_log_7',
    '{}',
    3,
    'taxi'
),
(
    'object_id_8',
    4,
    'antonvasyuk',
    'some_object',
    'ticket-4',
    '2022-01-28:09:00:00',
    'set_log_8',
    '{}',
    4,
    'taxi'
),
(
    'object_id_9',
    3,
    'antonvasyuk',
    'some_object',
    'ticket-5',
    '2022-02-01:15:00:00',
    'set_log_9',
    '{}',
    3,
    'taxi'
),
(
    'object_id_10',
    2,
    'antonvasyuk',
    'some_object',
    'ticket-6',
    '2022-02-02:15:00:00',
    'set_log_10',
    '{}',
    3,
    'taxi'
);
