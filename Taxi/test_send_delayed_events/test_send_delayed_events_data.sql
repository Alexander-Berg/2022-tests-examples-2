INSERT INTO eats_restapp_communications.send_event_data (
    event_id,
    event_type,
    event_mode,
    recipients,
    data,
    masked_data,
    created_at,
    updated_at,
    deleted_at
) VALUES (
    '1',
    'password-request-reset',
    'asap',
    '{"emails_types": [], "recipients": {"partnerish_uuids": ["1a"]}}'::JSONB,
    '{}'::JSONB,
    NULL,
    '2022-05-01T09:40:00+0300'::TIMESTAMPTZ,
    '2022-05-01T09:40:00+0300'::TIMESTAMPTZ,
    '2022-05-01T10:00:00+0300'::TIMESTAMPTZ
),
(
    '2',
    'password-request-reset',
    'delayed',
    '{"emails_types": [], "recipients": {"partnerish_uuids": ["1a"]}}'::JSONB,
    '{}'::JSONB,
    NULL,
    '2022-05-01T09:40:00+0300'::TIMESTAMPTZ,
    '2022-05-01T09:40:00+0300'::TIMESTAMPTZ,
    '2022-05-01T10:00:00+0300'::TIMESTAMPTZ
),
(
    '3',
    'password-request-reset',
    'delayed',
    '{"emails_types": [], "recipients": {"partnerish_uuids": ["1a"]}}'::JSONB,
    '{}'::JSONB,
    NULL,
    '2022-05-01T09:50:30+0300'::TIMESTAMPTZ,
    '2022-05-01T09:58:30+0300'::TIMESTAMPTZ,
    NULL
),
(
    '4',
    'password-request-reset',
    'delayed',
    '{"emails_types": [], "recipients": {"partnerish_uuids": ["1a"]}}'::JSONB,
    '{}'::JSONB,
    NULL,
    '2022-05-01T09:50:30+0300'::TIMESTAMPTZ,
    '2022-05-01T09:57:30+0300'::TIMESTAMPTZ,
    NULL
),
(
    '5',
    'password-request-reset',
    'delayed',
    '{"emails_types": [], "recipients": {"partnerish_uuids": ["1a"]}}'::JSONB,
    '{}'::JSONB,
    NULL,
    '2022-05-01T10:49:30+0300'::TIMESTAMPTZ,
    '2022-05-01T09:58:30+0300'::TIMESTAMPTZ,
    NULL
),
(
    '6',
    'password-request-reset',
    'delayed',
    '{"emails_types": [], "recipients": {"partnerish_uuids": ["1a"]}}'::JSONB,
    '{}'::JSONB,
    NULL,
    '2022-05-01T09:40:00+0300'::TIMESTAMPTZ,
    '2022-05-01T09:40:00+0300'::TIMESTAMPTZ,
    NULL
),
(
    '7',
    'password-request-reset',
    'delayed',
    '{"emails_types": [], "recipients": {"partnerish_uuids": ["1a"]}}'::JSONB,
    '{}'::JSONB,
    NULL,
    '2022-05-01T09:09:40+0300'::TIMESTAMPTZ,
    '2022-05-01T09:09:40+0300'::TIMESTAMPTZ,
    NULL
),
(
    '8',
    'password-request-reset',
    'delayed',
    '{"emails_types": [], "recipients": {"partnerish_uuids": ["1a"]}}'::JSONB,
    '{}'::JSONB,
    NULL,
    '2022-05-01T09:40:00+0300'::TIMESTAMPTZ,
    '2022-05-01T09:40:30+0300'::TIMESTAMPTZ,
    NULL
);
