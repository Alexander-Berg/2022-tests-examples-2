INSERT INTO crm_admin.campaign
(
    id,
    name,
    entity_type,
    trend,
    kind,
    discount,
    state,
    owner_name,
    ticket,
    ticket_status,
    is_regular,
    schedule,
    regular_start_time,
    regular_stop_time,
    created_at
)
VALUES
(
    1001,
    'regular campaign',
    'User',
    'trend',
    'kind',
    True,
    'NEW',
    'user',
    'ticket',
    'open',
    True,
    '* */1 * * *',
    '2021-01-01 00:00:00',
    '2021-01-11 00:00:00',
    '2020-12-29 01:00:00'
);
