insert into audit_events.systems (
    name
)
values (
    'exists_system'
),
(
    'tplatform'
);

insert into audit_events.actions (
    action,
    system_id
)
values (
    'exists_action',
    1
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
    'exist_log_1',
    1,
    'deoevgen',
    'create_test_logins_1',
    'ticket-1',
    '2020-11-27:00:00:00',
    'exist_request_id_1',
    '{"_id": "1", "body": {"a": "wat?"}, "request": {"home_zone": "ru"}}',
    1,
    null
),
(
    'exist_log_2',
    1,
    'deoevgen',
    'create_test_logins_2',
    'ticket-1',
    '2020-11-28:00:00:00',
    'exist_request_id_2',
     '{
      "_id": "2",
      "body": {
        "a": "wat?"
      }
    }',
    1,
    null
),
(
    'exist_log_3',
    1,
    'antonvasyuk',
    'create_test_logins_3',
    'ticket-2',
    '2022-01-14:14:00:00',
    'exist_request_id_3',
     '{}',
    2,
    'taxi'
);
