INSERT INTO pro_business_events.events (
    id,
    profile_id,
    title,
    platform_consumer,
    deeplink,
    event_date,
    external_id
) VALUES (
    'id_1',
    'profile_id_1',
    'title_1',
    'Market',
    'deeplink_1',
    '2001-12-12T10:00:00+00:00',
    'idempotency_token_1'
), (
    'id_2',
    'profile_id_2',
    'title_2',
    'Market',
    'deeplink_2',
    '2001-12-12T10:00:00+00:00',
    'idempotency_token_2'
), (
    'id_3',
    'profile_id_3',
    'title_3',
    'Lavka',
    NULL,
    '2001-12-12T10:00:00+00:00',
    'idempotency_token_3'
);
