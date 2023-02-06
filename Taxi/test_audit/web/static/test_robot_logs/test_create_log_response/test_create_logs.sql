insert into audit_events.systems (
    name
)
values (
    'exists_system'
),
(
    'tariff-editor'
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
    system_id
)
values (
    'exist_log',
    1,
    'deoevgen',
    'create_test_logins',
    'ticket-1',
    '2020-11-27:00:00:00',
    'exist_request_id',
     '{
      "_id": "1",
      "body": {
        "a": "wat?"
      }
    }',
    1
);
