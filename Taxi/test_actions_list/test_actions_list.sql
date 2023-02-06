insert into audit_events.systems (
    name
)
values (
    'system_1'
),
(
    'system_2'
),
(
    'system_3'
);

insert into audit_events.actions (
    action,
    system_id
)
values (
    'system_1_action_1',
    1
),
(
    'system_1_action_2',
    1
),
(
    'system_2_action_1',
    2
);
